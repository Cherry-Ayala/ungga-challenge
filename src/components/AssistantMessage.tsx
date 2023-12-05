import { useMemo, useEffect, useState } from 'react';
import MarkdownMessage from '@/components/MarkdownMessage';
import useMessagesStore from '@/store/useMessagesStore';
import FeedbackComponent from '@/stories/feedback/Feedback.component';

const AssistantMessage = ({
  content,
  contentId,
  showFeedbackMessage
}: {
  content: string;
  contentId: string;
  showFeedbackMessage: boolean;
}) => {
  const conversationsStorage = useMessagesStore((state) => state.messages);

  const isLastMessage = useMemo(() => {
    const assistanConversations = conversationsStorage.filter(
      (assistanConversation) => assistanConversation.role === 'assistant'
    );
    const lastMessageId = assistanConversations[assistanConversations.length - 1]?.id;
    return lastMessageId === contentId;
  }, [conversationsStorage, contentId]);

  const [userInput, setUserInput] = useState('');
  const [chatbotResponse, setChatbotResponse] = useState('');

  const sendUserInputToChatbot = () => {
    fetch('http://127.0.0.1:5000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_input: userInput }),
    })
      .then((response) => response.json())
      .then((data) => {
        setChatbotResponse(data.response);
      })
      .catch((error) => {
        console.error('Error:', error);
        setChatbotResponse('Error communicating with the chatbot.');
      });
  };

  useEffect(() => {
    if (isLastMessage) {
      // Automatically send a predefined message to the chatbot when it's the last message from the assistant
      setUserInput('Hello, schedule an appointment.');
    }
  }, [isLastMessage]);

  return (
    <div className='flex-1 flex flex-col item-start justify-between md:max-w-[80%] gap-3'>
      <MarkdownMessage id={contentId} content={content} />
      <input
        type="text"
        value={userInput}
        onChange={(e) => setUserInput(e.target.value)}
        placeholder="Type your message here"
      />
      <button onClick={sendUserInputToChatbot}>Send</button>
      <p>Chatbot Response: {chatbotResponse}</p>
      <FeedbackComponent showFeedbackMessage={showFeedbackMessage} isLastMessage={isLastMessage} />
    </div>
  );
};

export default AssistantMessage;

