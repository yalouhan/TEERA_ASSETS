let allSessions = []; 
let currentSession = [];

const inputBox = document.getElementById('account');


inputBox.addEventListener('keydown', function(event) {
    const keyInfo = {
        key: event.key,
        type: 'keydown',
        time: Date.now()
    };

    if (event.key === ' ')
        keyInfo.key = 'space';
    if (event.key === ',')
        keyInfo.key = ',';

    if (event.key === 'Tab') {
        return;
    }else if(event.key === 'Enter') {
        inputBox.value = '';
        allSessions.push({ 
        sessionId: allSessions.length + 1, 
        data: currentSession 
    });
        currentSession = [];
    }
    
});

inputBox.addEventListener('keyup', function(event) {
    const keyInfo = {
        key: event.key,
        type: 'keyup',
        time: Date.now()
    };

    if (event.key === ' ')
        keyInfo.key = 'space';
    if (event.key === ',')
        keyInfo.key = ',';

    if (event.key === 'Enter' || event.key === 'Tab') {
        return;
    }else{
         currentSession.push(keyInfo);
    }
});

document.getElementById('teera').addEventListener('click', function() {
    inputBox.value = '';
    allSessions.push({ 
    sessionId: allSessions.length + 1, 
    data: currentSession 
    });
    currentSession = [];
});

