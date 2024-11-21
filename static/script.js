const startMic = document.getElementById('start-mic');
const responseContainer = document.getElementById('recorder-container');
const titleContainer = document.getElementById('title-container');
const container2 = document.getElementById('container-2');
const stat = document.getElementById('status');
const response = document.querySelector('.response');

const uname = document.querySelector('#uname');


setTimeout(() => responseContainer.style.opacity = '1', 1000);


let recorder;
let audioStream;
let audioQueue = [];
let intermediateBuffer = [];

async function start_recording() {
            startMic.disabled = true;
            container2.querySelectorAll("h2")[1].innerText = "Listening ...";
            document.getElementById('status').disabled = false;


            navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                const mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start(5000);

                mediaRecorder.addEventListener("dataavailable", event => {
                    const audioBlob = new Blob([event.data], {type: 'audio/wav'});

                    const reader = new FileReader(); 
                    reader.readAsArrayBuffer(audioBlob); 
                    reader.onloadend = function() { 
                           console.log(audioBlob.size)
                           const arrayBuffer = reader.result;
                           const uint8Array = new Uint8Array(arrayBuffer); 
                                    // Add data to intermediate buffer 
                           intermediateBuffer = intermediateBuffer.concat(Array.from(uint8Array));
                                // Convert Blob to binary string and push to queue
                                console.log(intermediateBuffer.length)
                                while (intermediateBuffer.length >= 2048) { 
                                    const chunk = new Uint8Array(intermediateBuffer.slice(0, 2048)); 
                                    intermediateBuffer = intermediateBuffer.slice(2048);
                                         //  sendChunkToServer(chunk.buffer);
                                    audioQueue.unshift(chunk.buffer);
                                }
                           
                    // audioQueue.upshift(Blob);
                    // let reader = new FileReader();
                    //             reader.readAsArrayBuffer(audioBlob);
                    //             reader.onloadend = function() {
                    //                 let binaryString = reader.result;
                    //                 audioQueue.unshift(binaryString);
                    //                 logAudioChunk(binaryString);
                    //             };
                  
                }});
            });



            // Get access to the microphone
        //     try {
        //     audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        //     console.log('Microphone access is granted')
        //     // Initialize the recorder
        //     recorder = new RecordRTC(audioStream, {
        //         type: 'audio',
        //         recorderType: RecordRTC.StereoAudioRecorder,
        //         mimeType: "audio/wav",
        //         numberOfAudioChannels: 1,
        //         // bufferSize: 512,
        //         sampleRate: 44100,
        //         timeSlice: 10,
        //         ondataavailable: function(Blob) {

        //             const reader = new FileReader(); 
        //             reader.readAsArrayBuffer(Blob); 
        //             reader.onloadend = function() { 
        //                 const arrayBuffer = reader.result;
        //                 const uint8Array = new Uint8Array(arrayBuffer); 
        //                 // Add data to intermediate buffer 
        //                 intermediateBuffer = intermediateBuffer.concat(Array.from(uint8Array));
        //             // Convert Blob to binary string and push to queue
        //             while (intermediateBuffer.length >= 2048) { 
        //                 const chunk = new Uint8Array(intermediateBuffer.slice(0, 2048)); 
        //                 intermediateBuffer = intermediateBuffer.slice(2048);
        //                 //  sendChunkToServer(chunk.buffer);
        //                  audioQueue.unshift(chunk.buffer);
        //                  }
        //             // console.log(Blob)
        //             // let reader = new FileReader();
        //             // reader.readAsArrayBuffer(Blob);
        //             // reader.onloadend = function() {
        //             //     let binaryString = reader.result;
        //             //     audioQueue.unshift(binaryString);
        //             //     logAudioChunk(binaryString);
        //             // };
        //         }
        //     }});

        //     // Start recording
        //     recorder.startRecording();
        // }
        // catch (err){
        //     console.log('Microphone access is denied')
        // }

        };

function stopRecording(){
    recorder.stopRecording(function() {
        // Release microphone
        container2.querySelectorAll("h2")[1].innerText = " ... ";
        stat.innerHTML = '<i class="fa-regular fa-circle-pause"></i>';
        audioStream.getTracks().forEach(track => track.stop());
    });
    stat.onclick = async ()=>{
        startMic.onclick();
    }
    

}

   
    function logAudioChunk(binaryString) {
            // const logDiv = document.getElementById('log');
            console.log(`Audio chunk received Length: ${binaryString.byteLength}`);
        }



async function connect_ws(user_id){

    return new Promise((resolve, reject) => {
    const socket = new WebSocket('ws://localhost:5001/ws/'+user_id);
    socket.onopen = function(event) { 
        resolve(socket)
     }; 
    
    // Connection closed event 
    socket.onclose = function(event) { 
        console.log('WebSocket is closed.'); 
    }; 
    
    // Error event 
    socket.onerror = function(error) { 
        console.error('WebSocket error:', error); 
        reject(error)
    };
    
    socket.onmessage = function(event) { 
        console.log('Message from server:', event.data);
        receiveResponses(event.data)
        // const messagesDiv = document.getElementById('messages');
        // messagesDiv.innerHTML += `<p>${event.data}</p>`; 
    };
    
   });

}

async function start_connection(){
    try { 
        const socket = await connect_ws('your_user_id'); 
        console.log('WebSocket connected successfully.'); // Example of sending a message through WebSocket 
        
        setInterval(()=>{
            if(audioQueue.length !=0)
              socket.send(audioQueue.pop()); 
            else{
             console.log('audioQueue is empty!')
            }
        },100)
        
        }
       
     
    catch (error) { 
        console.error('Error during WebSocket connection:', error); 
    }
}



function scrollToBottom() { 
    response.scrollTo({ top: response.scrollHeight, behavior: 'smooth' }); 
}

function receiveResponses(message) 
{     
     const e = response.querySelectorAll('.assistant');
     if(message.responseType == 'user')
     {      
             response.innerHTML = response.innerHTML + `<div class="user"><div>${message.text}</div></div><div class="assistant"><div><i class="fa-solid fa-spinner fa-spin"></i></div></div>`;
     }
     else if(message.responseType == 'assistant' && message.text == 'CALL DALL-E')
     {   
       
         e[e.length-1].innerHTML = `<div></div><div class = 'image_process'><div><i class="fa-solid fa-spinner fa-spin"></i></div></div><div class="revised-prompt"></div>`;
         e[e.length-1].querySelector('div').innerText = 'Generating image ...';

         // response.innerHTML = response.innerHTML + `<div class="assistant"></div>`;
     }
     else if('image_url' in message)
     {
         e[e.length-1].querySelector('.image_process').innerHTML = `<img src="${message.image_url}" alt="Not found">`;
         e[e.length-1].querySelector('.revised-prompt').innerText =  message.revised_prompt
     }
    
     else if(message.responseType == 'assistant')
     {  
        e[e.length-1].querySelector('div').innerText = `${message.text}`;
     }
     else
        
         e[e.length-1].innerHTML =`<div>Content Policy Violation</div>`;
         
     console.table(message)
     scrollToBottom()
         
 // document.getElementById("status").innerText = "hello";
 }



startMic.onclick = async function () {
    
    titleContainer.style.opacity = '0';
    response.style.opacity = '1';

    container2.style.opacity= '1';
    container2.querySelectorAll("h2")[1].innerText = "Listening ...";
    stat.innerHTML = `<i class="fa-sharp fa-solid fa-circle-notch fa-spin"></i>`;

    responseContainer.style.cssText = `
                               width: 90vw;
                               height: 80vh;
                               opacity: 1;
                              `;
 
    
 
    setTimeout(async ()=>{
        titleContainer.style.display = 'none';
        container2.style.gap = '40px';
        container2.querySelectorAll("h2").forEach(e=>{
         e.style.opacity = '1';
        })

      start_recording();
      start_connection();

    }, 2000)

    stat.onclick = async ()=>{
        stopRecording();
   }

};


