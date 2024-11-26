const startMic = document.getElementById('start-mic');
const responseContainer = document.getElementById('recorder-container');
const titleContainer = document.getElementById('title-container');
const container2 = document.getElementById('container-2');
const strm = document.getElementById('stream');
const response = document.querySelector('.response');

const uname = document.querySelector('#uname');


setTimeout(() => responseContainer.style.opacity = '1', 1000);


let recorder;
let audioStream;
let mediaRecorder;
let audioQueue = [];
let intermediateBuffer = [];
let interval;

async function start_recording() {
           
            startMic.disabled = true;
            container2.querySelectorAll("h2")[1].innerText = "Listening ...";
            document.getElementById('status').disabled = false;

            // Get access to the microphone
            try {
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true});
            console.log('Microphone access is granted')

            
            // Initialize the recorder
            recorder = new RecordRTC(audioStream, {
                type: 'audio',
                recorderType: RecordRTC.StereoAudioRecorder,
                mimeType: "audio/wav",
                numberOfAudioChannels: 1,
                desiredSampRate: 16000,
                bufferSize: 1024,
                timeSlice: 100,
                ondataavailable: function(Blob) {
                    const reader = new FileReader();
                    reader.onloadend = async function() { 
                        const audio_bytes = reader.result;
                        audioQueue.unshift(audio_bytes)
                        
                        };
                    reader.readAsArrayBuffer(Blob);
                    
                }
            });

            // Start recording
            recorder.startRecording();
        }
        catch (err){
            console.log('Microphone access is denied')
        }
    }
      

function stopRecording(){
    recorder.stopRecording(function() {
        // Release microphone
        container2.querySelectorAll("h2")[1].innerText = " ... ";
        strm.innerHTML = '<i class="fa-regular fa-circle-pause"></i>';
        audioStream.getTracks().forEach(track => track.stop());
        clearInterval(interval)
    });
    strm.onclick = async ()=>{
        startMic.onclick();
    }
    

}



async function connect_ws(user_id){

    return new Promise((resolve, reject) => {
    const socket = new WebSocket(`wss://${window.location.hostname}:${window.location.port}/ws/`+user_id);
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
        const socket = await connect_ws('Akshat'); 
        console.log('WebSocket connected successfully.'); // Example of sending a message through WebSocket 
        
        interval = setInterval(()=>{
                    if(audioQueue.length !=0)
                   {
                        if (socket.readyState === WebSocket.OPEN) {
                            socket.send(audioQueue.pop());
                        } 
                     else { 
                            container2.querySelectorAll("h2")[1].innerText = "Disconnected ...";
                        }
                      } 
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
     message = JSON.parse(message)
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
     else if('Recieved' in message)
        {  
            console.log(`${message.Recieved}`);
            return 0;
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
    strm.innerHTML = `<i class="fa-sharp fa-solid fa-circle-notch fa-spin"></i>`;

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

    strm.onclick = async ()=>{
        stopRecording();
   }

};


