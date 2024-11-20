const startMic = document.getElementById('start-mic');
const responseContainer = document.getElementById('recorder-container');
const titleContainer = document.getElementById('title-container');
const container2 = document.getElementById('container-2');
const stat = document.getElementById('status');
const response = document.querySelector('.response');

const uname = document.querySelector('#uname');


setTimeout(() => responseContainer.style.opacity = '1', 1000);



function connect_ws(user_id){
    const socket = new WebSocket('ws://localhost:5001/ws/'+user_id);
    socket.onopen = function(event) { 
        console.log('WebSocket is connected.');
     }; 
    
    // Connection closed event 
    socket.onclose = function(event) { 
        console.log('WebSocket is closed.'); 
    }; 
    
    // Error event 
    socket.onerror = function(error) { 
        console.error('WebSocket error:', error); 
    };
    
    socket.onmessage = function(event) { 
        console.log('Message from server:', event.data);
        // const messagesDiv = document.getElementById('messages');
        // messagesDiv.innerHTML += `<p>${event.data}</p>`; 
    };

}

connect_ws('Akshat');

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



//3)
startMic.onclick = async function() {

    titleContainer.style.opacity = '0';
    response.style.opacity = '1';
 //    status.style.border = '1px solid black'
    container2.style.opacity= '1';
   
    responseContainer.style.cssText = `
                               width: 90vw;
                               height: 80vh;
                               opacity: 1;
                              `;
 
    
 
    setTimeout(()=>{
        titleContainer.style.display = 'none';
        container2.style.gap = '40px';
        container2.querySelectorAll("h2").forEach(e=>{
         e.style.opacity = '1';
        })
    }, 2000)

};

stat.onclick = async ()=>{
     startMic.click();
}

