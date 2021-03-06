// Mojia & Harshita
// final project
// beta version
// Dec 19, 2017

// This Javascript file adds the audio recording functionality to the page.
// In orer to recourd audio, the browser must first get permission from the
// user to access the raw audio input from the microphone, which is done
// using getUserMedia. After recording starts, the API collects audio snippets
// at regular increments of time from 'input channels', and stores them locally.
// Once recording is complete ('End Conversation' button is clicked), the recorder
// auditomatically stops recording, and saves the recording. This is done by combining
// all the audio snippets from the left and right stream as a Blob, and then
// saving the file remotely using a unique route using AJAX. (Right now, we also save the
// file to the local device (user's computer) for sanity check, but will remove that
// in the Beta version). Then, a listener implemented in Flask will fetch the file, and
// save to the server (this is yet to be implemented).

// script adapted from https://gist.github.com/meziantou/edb7217fddfbb70e899e

//extract convoId and userId
var convoId = document.currentScript.getAttribute('convoId'); //1
var userId = document.currentScript.getAttribute('userId'); //2

var startRecordingButton = document.getElementById("startRecordingButton");
var stopRecordingButton = document.getElementById("end");
var leftchannel = [];
var rightchannel = [];
var recorder = null;
var recordingLength = 0;
var volume = null;
var mediaStream = null;
var sampleRate = 44100;
var context = null;
var blob = null;
startRecordingButton.addEventListener("click", function () {

// Initialize recorder
navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
navigator.getUserMedia(
{
    audio: true
},
function (e) {

console.log("user consent");
// creates the audio context
window.AudioContext = window.AudioContext || window.webkitAudioContext;
context = new AudioContext();
// creates an audio node from the microphone incoming stream
mediaStream = context.createMediaStreamSource(e);
// https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/createScriptProcessor
// bufferSize: the onaudioprocess event is called when the buffer is full
var bufferSize = 2048;
var numberOfInputChannels = 2;
var numberOfOutputChannels = 2;
if (context.createScriptProcessor) {
    recorder = context.createScriptProcessor(bufferSize, numberOfInputChannels, numberOfOutputChannels);
} else {
    recorder = context.createJavaScriptNode(bufferSize, numberOfInputChannels, numberOfOutputChannels);
}
recorder.onaudioprocess = function (e) {
    leftchannel.push(new Float32Array(e.inputBuffer.getChannelData(0)));
    rightchannel.push(new Float32Array(e.inputBuffer.getChannelData(1)));
    recordingLength += bufferSize;
}
// we connect the recorder
mediaStream.connect(recorder);
recorder.connect(context.destination);
},
function (e) {
    console.error(e);
});
    });

stopRecordingButton.addEventListener("click", function () {

    // stop recording
    recorder.disconnect(context.destination);
    mediaStream.disconnect(recorder);
    // we flat the left and right channels down
    // Float32Array[] => Float32Array
    var leftBuffer = flattenArray(leftchannel, recordingLength);
    var rightBuffer = flattenArray(rightchannel, recordingLength);
    // we interleave both channels together
    // [left[0],right[0],left[1],right[1],...]
    var interleaved = interleave(leftBuffer, rightBuffer);
    // we create our wav file
    var buffer = new ArrayBuffer(44 + interleaved.length * 2);
    var view = new DataView(buffer);
    // RIFF chunk descriptor
    writeUTFBytes(view, 0, 'RIFF');
    view.setUint32(4, 44 + interleaved.length * 2, true);
    writeUTFBytes(view, 8, 'WAVE');
    // FMT sub-chunk
    writeUTFBytes(view, 12, 'fmt ');
    view.setUint32(16, 16, true); // chunkSize
    view.setUint16(20, 1, true); // wFormatTag
    view.setUint16(22, 2, true); // wChannels: stereo (2 channels)
    view.setUint32(24, sampleRate, true); // dwSamplesPerSec
    view.setUint32(28, sampleRate * 4, true); // dwAvgBytesPerSec
    view.setUint16(32, 4, true); // wBlockAlign
    view.setUint16(34, 16, true); // wBitsPerSample
    // data sub-chunk
    writeUTFBytes(view, 36, 'data');
    view.setUint32(40, interleaved.length * 2, true);
    // write the PCM samples
    var index = 44;
    var volume = 1;
    for (var i = 0; i < interleaved.length; i++) {
        view.setInt16(index, interleaved[i] * (0x7FFF * volume), true);
        index += 2;
    }
    // our final blob
    var blob = new Blob([view], { type: 'audio/wav' });

    //add functionality of download to end of stop button
    if (blob == null) {
        return;
    }

    // pass blob in a FormData to flask
    var form = new FormData();
    // create filename
    filename = userId+"_"+convoId+".wav"

    form.append('blob', blob, filename);
    console.log('this is the blob', blob)

    var audiourl = '/audiofile/' + userId + '/'+convoId + '/';
    console.log('this is the audiourl', audiourl);

    var redirectLink = '/feedback/'+convoId

    //post file to route
    $.ajax({
      type: "POST",
      url: audiourl,
      data: form,
      processData: false,
      contentType: false,
      dataType: 'audio/wav',
      success: function(e){
        console.log("success");
        // success is not being entered, and cannot redirect within success
        // window.location.href = redirectLink;
        return 1;
        },
      complete: function(f){
            console.log("ajax complete");
            //redirect to feedback page within complete instead
            window.location.href = redirectLink;
            return 1;
        },
        error: function(e){
            console.log('error', e)
        }
    })

});

//helper functions adapted from code found on Github
function flattenArray(channelBuffer, recordingLength) {
    var result = new Float32Array(recordingLength);
    var offset = 0;
    for (var i = 0; i < channelBuffer.length; i++) {
        var buffer = channelBuffer[i];
        result.set(buffer, offset);
        offset += buffer.length;
    }
    return result;
}
function interleave(leftChannel, rightChannel) {
    var length = leftChannel.length + rightChannel.length;
    var result = new Float32Array(length);
    var inputIndex = 0;
    for (var index = 0; index < length;) {
        result[index++] = leftChannel[inputIndex];
        result[index++] = rightChannel[inputIndex];
        inputIndex++;
    }
    return result;
}
function writeUTFBytes(view, offset, string) {
    for (var i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}
