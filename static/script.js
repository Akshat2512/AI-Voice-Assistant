const start = document.getElementById('start-mic');
const responseContainer = document.getElementById('message-container');
const titleContainer = document.getElementById('title-container');
const sendContainer = document.getElementById('send-container');
const listener = document.getElementById('listener');
const writer = document.getElementById('writer');
const fa_keyboard = document.getElementById('fa-keyboard');
const strm = document.getElementById('stream');
const response = document.querySelector('.response');
const ws_status = document.querySelector('#status');
const uname = document.querySelector('#uname');
const send = document.querySelector('#send');

setTimeout(() => {
    username = localStorage.getItem('uname');
    uname.value = username;
    responseContainer.style.opacity = '1'
}, 1000);


let recorder;
let audioStream;
let mediaRecorder;
let audioQueue = [];
let socket;
let interval;

let  i = 0
async function start_recording() {
            
            start.disabled = true;
            strm.innerHTML = `<i class="fa-solid fa-microphone fa-fade"></i>`;

            // Get access to the microphone
            try {
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true});
            console.log('Microphone access is granted')
            strm.style.opacity = '1';
            
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
                        audioQueue.unshift(audio_bytes);
                        };
                    reader.readAsArrayBuffer(Blob);
                    
                }
            });

            // Start recording
            recorder.startRecording();

            interval = setInterval(()=>{
                if(audioQueue.length !=0)
               {
                    if (socket.readyState === WebSocket.OPEN) {
                        socket.send(audioQueue.pop());
                    } 
                    else { 
                      ws_status.innerText = "Disconnected";
                      ws_status.style.backgroundColor = "grey";
                    }
                } 
                else
                {
                console.log('audioQueue is empty!')
                }

                strm.onclick = ()=>{
                    flag = 1;
                    fa_keyboard.style.zIndex='1';
                    stop_recording();
                    console.log(flag)
                }
      
    },100)

    setTimeout(async ()=>{
        
        listener.style.gap = '40px';
        listener.querySelectorAll("h2").forEach(e=>{
         e.style.opacity = '1';
        })

    })

        }
        catch (err){
            console.log('Microphone access is denied')
        }
    }

let flag = 0
function stop_recording(){
    try{
    
    recorder.stopRecording();
  
    strm.innerHTML = '<i class="fa-solid fa-microphone"></i>';
    audioStream.getTracks().forEach(track => track.stop());
    clearInterval(interval);
    
    setTimeout(async ()=>{
        listener.style.gap = '80px';
        listener.querySelectorAll("h2").forEach(e=>{
         e.style.opacity = '0';
        })

    })

    }
    catch(e){

    }
    strm.onclick = ()=>{
        flag = 0;
        fa_keyboard.style.zIndex='0';
        start_recording();
        console.log(flag)
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
        ws_status.innerText = "Disconnected";
        ws_status.style.backgroundColor = "grey";
    }; 
    
    // Error event 
    socket.onerror = function(error) { 
        console.error('WebSocket error:', error); 
        reject(error)
    };
    
    socket.onmessage = function(event) { 
        
        console.log('Message from server:', event.data);
        if (flag == 0)
         receiveResponses(event.data);
        // const messagesDiv = document.getElementById('messages');
        // messagesDiv.innerHTML += `<p>${event.data}</p>`; 
    };
    
   });

}

async function start_connection(){
  
    try { 
        socket = await connect_ws(uname.value); 
        console.log('WebSocket connected successfully.'); // Example of sending a message through WebSocket 
        ws_status.innerText = "Connected";
        ws_status.style.backgroundColor = "green";
        ws_status.style.opacity = '1';
        sendContainer.style.opacity= '1';
        sendContainer.style.pointerEvents= 'visible';
        onStartup();
        // stop_recording();
        }
       
    catch (error) { 
            console.error('Error during WebSocket connection:', error); 
            ws_status.innerText = "Disconnected";
            ws_status.style.backgroundColor = "grey";
            ws_status.style.opacity = '1'; 
            start_connection();    //if failed then keep trying connecting
    }

}

function closeWriter(){
    setTimeout(start_recording, 1000)
    fa_keyboard.style.zIndex='0';
    writer.style.opacity = "0";
    writer.style.pointerEvents='none';
    writer.style.width = "35%";
    
    fa_keyboard.style.width = '50px';
    listener.style.right = '50%';
    
}

function closeListener(){
    writer.style.opacity = "1";
    writer.style.pointerEvents='visible';
    writer.style.width = "100%";
    
    fa_keyboard.style.width = '0px';
    listener.style.right = '0%';
    
    stop_recording();
    onStartup();
}

function onStartup(){
    strm.onclick = closeWriter;
    fa_keyboard.onclick = closeListener;
}

function scrollToBottom(){ 
    response.scrollTo({ top: response.scrollHeight, behavior: 'smooth' }); 
}

function receiveResponses(message) 
{     
     const e = response.querySelectorAll('.assistant');
     message = JSON.parse(message)
     if(message.responseType == 'user')
     {      
             while_ai_prompt_generating();
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
         after_ai_prompt_generated();
         e[e.length-1].querySelector('.image_process').innerHTML = `<img src="${message.image_url}" alt="Not found">`;
         e[e.length-1].querySelector('.revised-prompt').innerText =  message.revised_prompt
     }
    
     else if(message.responseType == 'assistant')
     {  
        after_ai_prompt_generated();
        e[e.length-1].querySelector('div').innerText = `${message.text}`;
     }
 
     else if(message.status == 'error'){
        // recorder.startRecording();
        after_ai_prompt_generated();
        e[e.length-1].innerHTML =`<div>Content Policy Violation</div>`;
     }
        
         
     console.table(message)
     scrollToBottom()
         
 // document.getElementById("status").innerText = "hello";
 }



start.onclick = async function () {

    if (uname.value == '')
    {
        alert('Please enter username !!');
        return false;
    }
    else
    {   
        localStorage.setItem('uname', uname.value);
    }

    titleContainer.style.opacity = '0';
    response.style.opacity = '1';

    responseContainer.style.cssText = `
                               width:80%;
                               height: 70%;
                               opacity: 1;
                              `;
    setTimeout(async ()=>{
        titleContainer.style.display = 'none';
        start_connection();
    }, 2000);
     
    
};


function while_ai_prompt_generating(){
    if(writer.style.opacity == '0')
     {  
          stop_recording();
          strm.onclick = null;
          fa_keyboard.style.zIndex='1';
     }
        
}

function after_ai_prompt_generated(){
    if(writer.style.opacity == '0')
        {   
            start_recording();
            fa_keyboard.style.zIndex='0';
        }
}

send.onclick = ()=>{
    const message = writer.querySelector('textarea');
    flag = 0;
    if (message.value != ''){
       socket.send(message.value);
       message.value = '';
    }
    
}
