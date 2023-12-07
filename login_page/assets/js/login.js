let currentSession = [];
export function initLogin(){
    document.querySelector('#teera').addEventListener('click', event => {
        event.preventDefault();
        login();
        const inputBox = document.getElementById('account');
        inputBox.value = '';
    });
}

function login(){
    var username = document.querySelector('#account').value;
    var password = document.querySelector('#password').value;
    var keystrokes = currentSession;
    const headers = {'Content-Type':'application/json',
                    'Access-Control-Allow-Origin':'*',
                    'Access-Control-Allow-Methods':'POST,PATCH,OPTIONS'}
    fetch('http://127.0.0.1:5000/analyze', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
            username: username,
            keystrokes: keystrokes
        }),
    })
    .then(response => response.json())
    .then(data => {
        if(data){
            console.log(data);
            window.location.href = '/helloworld.html';
        }else{
            console.log(data);
            window.location.href = '/verify-false.html';
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function initCollectKeystrokes(){
    const inputBox = document.getElementById('account');
    inputBox.addEventListener('keydown', function(event) {
        const keyInfo = {
            key: event.key,
            type: 'keydown',
            time: Date.now()
        };

        if (event.key === ' '){
            keyInfo.key = 'space';
            currentSession.push(keyInfo);
        }else if (event.key === ','){
            keyInfo.key = ',';
            currentSession.push(keyInfo);
        }
        else if (event.key === 'Tab') {
            return;
        }else if(event.key === 'Enter') {
            inputBox.value = '';
        }else{
            currentSession.push(keyInfo);
        }
        
    });

    inputBox.addEventListener('keyup', function(event) {
        const keyInfo = {
            key: event.key,
            type: 'keyup',
            time: Date.now()
        };

        if (event.key === ' '){
            keyInfo.key = 'space';
            currentSession.push(keyInfo);
        }else if (event.key === ','){
            keyInfo.key = ',';
            currentSession.push(keyInfo);
        }else if (event.key === 'Enter' || event.key === 'Tab') {
            return;
        }else{
            currentSession.push(keyInfo);
        }
    });

}

initCollectKeystrokes();
initLogin();