const startMic = document.getElementById('start-mic');
const responseContainer = document.getElementById('recorder-container');
const titleContainer = document.getElementById('title-container');
const container2 = document.getElementById('container-2');
const status = document.getElementById('status');
const response = document.querySelector('.response');

const uname = document.querySelector('#uname');


setTimeout(() => responseContainer.style.opacity = '1', 1000);
 

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
     else if(message.responseType == 'assistant' && message.text == 'Generating image ...')
     {   
         
         e[e.length-1].innerHTML = `<div></div><div class = 'image_process'><img src="${message.image_url}" alt="Not found"></div><div class="revised-prompt">${message.revised_prompt}</div>`;
         e[e.length-1].querySelector('div').innerText = `${message.text}`;
         // response.innerHTML = response.innerHTML + `<div class="assistant"></div>`;
     }
    
     else if(message.responseType == 'assistant')
     {  
        e[e.length-1].querySelector('div').innerText = `${message.text}`;
     }
     else
         e[e.length-1].innerText =`<div>${message}</div>`;
         
     console.table(message)
     scrollToBottom()
         
 // document.getElementById("status").innerText = "hello";
 }

eel.expose(receiveResponses);


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


    await eel.handle_connect('Akshat', 'start');
    console.log('start');

};


