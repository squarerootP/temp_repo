import '/src/index.css';
import { useState } from 'react';
import ChatHistory from "/src/data/chat_messages.json"
import ReactMarkdown from "react-markdown";

function ChatBotToggleButton() {
  const [isChatBotOpen, setChatBotOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "ai",
      content: "Helo! I'm Elib chatbot promax. How can I assist you today?"
    }
  ])

  function ChatBotBoxChat() {

    function toggleSubmitChat(e) {
      e.preventDefault();

      
    }


    return (
      <div className='fixed bottom-24 right-24 z-50 flex h-[500px] w-[400px] flex-col rounded-2xl border-[3px] border-green-700 bg-white shadow-lg'>
        {/* Header */}
        <div className='flex items-center justify-between rounded-t-xl bg-green-600 p-3 text-white'>
          <h2 className='text-lg font-bold'>Elib chatbot promax</h2>
          <button className='text-xl text-white hover:text-gray-200'>✕</button>
        </div>

        {/* Message area */}
        <div className='flex-1 space-y-2 overflow-y-auto bg-green-50 p-4'>
          {ChatHistory.messages.map((message, index) => (
            <div key={index} className={`${message.role}-message`}>
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          ))}
        </div>

        {/* Input area */}
        <div className='flex flex-row items-center border-t border-green-300 p-2'>
          <input
            type='text'
            placeholder='Type a message...'
            className='flex-1 rounded-lg border border-green-400 p-2 focus:outline-hidden'
          />
          <button className='ml-2 rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-600'>
            Send
          </button>
        </div>
      </div>
    );
  }

  function toggleChatBot() {
    setChatBotOpen(!isChatBotOpen);
  }
  return (
    <>
      <button
        className='fixed bottom-8 right-8 z-50 rounded-full border-4 border-white bg-green-600 p-4 text-white shadow-lg transition-colors hover:bg-green-700'
        onClick={toggleChatBot}
      >
        <img className='h-12 w-12' src='./src/assets/images/chatbot/robot.png' alt='' />
      </button>
      {isChatBotOpen && <ChatBotBoxChat />}
    </>
  );
}

export default ChatBotToggleButton;
