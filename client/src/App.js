import React, {useEffect} from 'react';
import '@chatui/core/es/styles/index.less';
import Chat, {Bubble, useMessages} from '@chatui/core';
import '@chatui/core/dist/index.css';

const App = () => {
    const {messages, appendMsg, setTyping} = useMessages([]);
    const [socket, setSocket] = React.useState(null);
    useEffect(() => {
        const socket = new WebSocket('ws://localhost:8000/ws');
        socket.onopen = function () {
            console.log('socket open');
        };
        socket.onmessage = function (e) {
            const data = e.data
            appendMsg({
                type: 'text',
                content: {text: data},
            })
        };
        socket.onclose = function () {
            console.log('socket close');
        };
        socket.onerror = function () {
            console.log('socket error');
        };
        setSocket(socket);
        return () => {
            socket.close();
        }
    }, []);

    function handleSend(type, val) {
        if (type === 'text' && val.trim()) {
            appendMsg({
                type: 'text',
                content: {text: val},
                position: 'right',
            });

            setTyping(true);

            if (socket) {
                socket.send(val);
            }
        }
    }

    function renderMessageContent(msg) {
        const {content} = msg;
        return <Bubble content={content.text}/>;
    }

    return (
        <Chat
            navbar={{title: 'ChatFlow'}}
            messages={messages}
            renderMessageContent={renderMessageContent}
            onSend={handleSend}
        />
    );
};
export default App;
