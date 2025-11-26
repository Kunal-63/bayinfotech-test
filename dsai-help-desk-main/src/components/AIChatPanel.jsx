// AIChatPanel - Main chat interface component
import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Alert,
  Collapse,
  Chip,
  Paper,
  alpha,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChatIcon from '@mui/icons-material/Chat';
import { styled } from '@mui/material/styles';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import chatService from '../services/chatService';

const ChatPanel = styled(Paper)(({ theme }) => ({
  position: 'fixed',
  bottom: 24,
  right: 24,
  width: '420px',
  height: 'calc(100vh - 112px)',
  maxHeight: '700px',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: '#1a1a1a',
  color: '#E0E0E0',
  borderRadius: '16px',
  border: `2px solid ${alpha('#D4AF37', 0.3)}`,
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.6), 0 4px 16px rgba(212, 175, 55, 0.2)',
  zIndex: 1000,
  background: `linear-gradient(180deg, ${alpha('#1a1a1a', 1)} 0%, ${alpha('#121212', 1)} 100%)`,
  overflow: 'hidden',
  [theme.breakpoints.down('lg')]: {
    width: '380px',
  },
  [theme.breakpoints.down('md')]: {
    width: 'calc(100vw - 48px)',
    right: 24,
    left: 24,
    height: 'calc(100vh - 112px)',
    maxHeight: '85vh',
  },
}));

const ChatHeader = styled(Box)(({ theme }) => ({
  padding: '20px 24px',
  borderBottom: `2px solid ${alpha('#D4AF37', 0.2)}`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  background: `linear-gradient(135deg, ${alpha('#D4AF37', 0.15)} 0%, ${alpha('#0052CC', 0.1)} 100%)`,
  borderRadius: '16px 16px 0 0',
  position: 'relative',
  '&::after': {
    content: '""',
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: '2px',
    background: `linear-gradient(90deg, transparent, ${alpha('#D4AF37', 0.6)}, transparent)`,
  },
}));

const MessagesContainer = styled(Box)(({ theme }) => ({
  flex: 1,
  overflowY: 'auto',
  padding: '20px',
  background: `linear-gradient(180deg, ${alpha('#1a1a1a', 1)} 0%, ${alpha('#121212', 1)} 100%)`,
  '&::-webkit-scrollbar': {
    width: '10px',
  },
  '&::-webkit-scrollbar-track': {
    backgroundColor: '#121212',
    borderRadius: '5px',
  },
  '&::-webkit-scrollbar-thumb': {
    backgroundColor: alpha('#D4AF37', 0.3),
    borderRadius: '5px',
    border: '2px solid #121212',
    '&:hover': {
      backgroundColor: alpha('#D4AF37', 0.5),
    },
  },
}));

const TypingIndicator = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: '10px',
  padding: '12px 16px',
  color: '#999999',
  backgroundColor: alpha('#333333', 0.3),
  borderRadius: '12px',
  border: `1px solid ${alpha('#D4AF37', 0.2)}`,
  marginBottom: '12px',
  width: 'fit-content',
}));

const AIChatPanel = ({ isOpen, onClose, onTicketCreated, initialMessage = null }) => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [typingMessage, setTypingMessage] = useState('Understanding request...');
  const [conversationContext, setConversationContext] = useState({});
  const [escalationStatus, setEscalationStatus] = useState(null);
  const [collapsed, setCollapsed] = useState(false);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const typingIntervalRef = useRef(null);
  const initialMessageSentRef = useRef(false);
  const lastInitialMessageRef = useRef(null);

  // Rotating typing messages
  const typingMessages = [
    'Understanding request...',
    'Analyzing...',
    'Processing...',
    'Generating response...',
  ];

  // Rotate typing messages when typing
  useEffect(() => {
    if (isTyping && !escalationStatus) {
      let messageIndex = 0;
      setTypingMessage(typingMessages[0]);

      typingIntervalRef.current = setInterval(() => {
        messageIndex = (messageIndex + 1) % typingMessages.length;
        setTypingMessage(typingMessages[messageIndex]);
      }, 1500);

      return () => {
        if (typingIntervalRef.current) {
          clearInterval(typingIntervalRef.current);
        }
      };
    } else {
      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
      }
    }
  }, [isTyping, escalationStatus]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Initialize with welcome message when chat is opened and not collapsed
  useEffect(() => {
    if (isOpen && !collapsed) {
      // Only initialize welcome message if messages array is empty
      if (messages.length === 0) {
        const welcomeMessage = {
          id: Date.now(),
          type: 'ai',
          content: "Hello! I'm your AI assistant for PCTE Help Desk. How can I help you today?",
          timestamp: new Date(),
          sentiment: { sentiment: 'neutral', score: 0 },
          confidence: 0.95,
        };
        setMessages([welcomeMessage]);
      }
    }
  }, [isOpen, collapsed, messages.length]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = useCallback(async (userMessage) => {
    // Add user message
    const userMsg = {
      id: Date.now(),
      type: 'user',
      content: userMessage,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);

    setIsTyping(true);

    try {
      // Call real backend API
      const response = await chatService.sendMessage(userMessage, 'trainee', conversationContext);

      if (response.success) {
        const formattedResponse = chatService.formatChatResponse(response.data);

        // Handle escalation
        if (formattedResponse.needsEscalation) {
          setEscalationStatus({
            message: 'Connecting to live agent...',
            status: 'escalating',
          });

          // Simulate escalation delay
          setTimeout(() => {
            setEscalationStatus({
              message: 'Agent connected: Sarah from Tier 1 Support',
              status: 'connected',
            });

            // Add agent message
            const agentMsg = {
              id: Date.now() + 2,
              type: 'agent',
              content: `Hi! I'm Sarah from Tier 1 Support. I see you're having an issue that requires attention. I'm here to help.`,
              timestamp: new Date(),
              agentName: 'Sarah',
              agentTier: 'Tier 1',
            };

            setMessages(prev => [...prev, agentMsg]);
            setEscalationStatus({
              message: 'Live agent active',
              status: 'active',
            });
          }, 2000);
        }

        // Add AI message
        const aiMsg = {
          id: Date.now() + 1,
          type: 'ai',
          content: formattedResponse.message,
          timestamp: new Date(),
          confidence: formattedResponse.confidence,
          sentiment: { sentiment: 'neutral', score: 0 }, // Backend doesn't return sentiment yet
          kbReferences: formattedResponse.kbReferences,
          guardrail: formattedResponse.guardrail,
          ticketId: formattedResponse.ticketId,
        };

        setMessages(prev => [...prev, aiMsg]);

        // If ticket was created (if backend supports it in future)
        if (formattedResponse.ticketId && onTicketCreated) {
          onTicketCreated({ id: formattedResponse.ticketId });
        }

      } else {
        // Handle API error
        const errorMsg = {
          id: Date.now() + 1,
          type: 'ai',
          content: `I apologize, but I encountered an error: ${response.error}. Please try again later.`,
          timestamp: new Date(),
          isError: true,
        };
        setMessages(prev => [...prev, errorMsg]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMsg = {
        id: Date.now() + 1,
        type: 'ai',
        content: "I'm having trouble connecting to the server. Please check your connection and try again.",
        timestamp: new Date(),
        isError: true,
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  }, [messages, conversationContext, onTicketCreated]);

  // Handle initial message and auto-expand when message is provided
  useEffect(() => {
    if (isOpen && initialMessage && initialMessage !== lastInitialMessageRef.current) {
      // Reset the sent flag for new initial message
      initialMessageSentRef.current = false;
      lastInitialMessageRef.current = initialMessage;

      // If chat is collapsed, expand it first
      if (collapsed) {
        setCollapsed(false);
      }
    } else if (!initialMessage) {
      // Clear refs when initial message is cleared
      initialMessageSentRef.current = false;
      lastInitialMessageRef.current = null;
    }
  }, [initialMessage, isOpen, collapsed]);

  // Send initial message after chat is expanded and welcome message is shown
  useEffect(() => {
    if (isOpen && !collapsed && initialMessage && !initialMessageSentRef.current) {
      // Wait for welcome message to be set if needed
      if (messages.length === 0) {
        // Welcome message will be set by the other useEffect, wait for it
        return;
      }

      // Welcome message exists, send the initial message
      const timer = setTimeout(() => {
        if (!initialMessageSentRef.current) {
          initialMessageSentRef.current = true;
          handleSendMessage(initialMessage);
        }
      }, 800);

      return () => clearTimeout(timer);
    }
  }, [isOpen, collapsed, initialMessage, messages.length, handleSendMessage]);

  const handleClose = () => {
    // Reset chat state and collapse (but don't close completely)
    setMessages([]);
    setConversationContext({});
    setEscalationStatus(null);
    setIsTyping(false);
    setCollapsed(true);
    initialMessageSentRef.current = false;
    lastInitialMessageRef.current = null;
    // Clear initial message in parent but keep chat open (so floating button shows)
    if (onClose) {
      // Only clear the initial message, don't close the chat
      onClose();
    }
  };

  const handleToggleCollapse = () => {
    const newCollapsedState = !collapsed;

    // Reset any stuck states when toggling
    setIsTyping(false);
    if (newCollapsedState) {
      // When collapsing, clear escalation status
      setEscalationStatus(null);
    }

    setCollapsed(newCollapsedState);
  };

  const handleOptionClick = (option) => {
    handleSendMessage(option);
  };

  if (!isOpen) return null;

  // When collapsed, show a floating button to reopen
  if (collapsed) {
    return (
      <Box
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          zIndex: 1000,
        }}
      >
        <IconButton
          onClick={handleToggleCollapse}
          sx={{
            width: 'auto',
            height: 56,
            minWidth: 180,
            px: 2,
            backgroundColor: '#D4AF37',
            color: '#1a1a1a',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(212, 175, 55, 0.4)',
            '&:hover': {
              backgroundColor: '#E8C547',
              boxShadow: '0 6px 16px rgba(212, 175, 55, 0.5)',
              transform: 'scale(1.05)',
            },
            transition: 'all 0.3s ease',
          }}
        >
          <ChatIcon sx={{ fontSize: '24px', mr: 1 }} />
          <Typography sx={{ fontWeight: 'bold', fontSize: '16px', textTransform: 'none' }}>
            Chat with ACE
          </Typography>
        </IconButton>
      </Box>
    );
  }

  return (
    <ChatPanel elevation={8}>
      <ChatHeader>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: '12px',
              background: `linear-gradient(135deg, ${alpha('#D4AF37', 0.3)} 0%, ${alpha('#0052CC', 0.2)} 100%)`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: `2px solid ${alpha('#D4AF37', 0.4)}`,
              boxShadow: `0 4px 12px ${alpha('#D4AF37', 0.2)}`,
            }}
          >
            <SmartToyIcon sx={{ color: '#D4AF37', fontSize: '24px' }} />
          </Box>
          <Box>
            <Typography variant="h6" sx={{ color: '#D4AF37', fontWeight: 'bold', fontSize: '18px', lineHeight: 1.2 }}>
              ACE - AI Assistant
            </Typography>
            <Typography variant="caption" sx={{ color: alpha('#E0E0E0', 0.7), fontSize: '11px' }}>
              Always here to help
            </Typography>
          </Box>
        </Box>
        <IconButton
          onClick={handleClose}
          sx={{
            color: '#999999',
            '&:hover': {
              backgroundColor: alpha('#D4AF37', 0.1),
              color: '#D4AF37',
            },
            transition: 'all 0.2s ease',
          }}
        >
          <CloseIcon />
        </IconButton>
      </ChatHeader>

      <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden' }}>
        <MessagesContainer ref={messagesContainerRef}>
          {messages.map((msg) => {
            return (
              <ChatMessage
                key={msg.id}
                message={msg.content}
                isUser={msg.type === 'user'}
                source={msg.source}
                confidence={msg.confidence}
                sentiment={msg.sentiment}
                type={msg.messageType === 'guardrail' ? 'guardrail' : null}
                agentName={msg.agentName}
                agentTier={msg.agentTier}
                isTyping={msg.isTyping}
                guardrail={msg.guardrail}
                kbReferences={msg.kbReferences}
              />
            );
          })}

          {isTyping && !escalationStatus && (
            <TypingIndicator>
              <Box
                sx={{
                  width: 24,
                  height: 24,
                  borderRadius: '50%',
                  background: `linear-gradient(135deg, ${alpha('#D4AF37', 0.3)} 0%, ${alpha('#0052CC', 0.2)} 100%)`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: `1px solid ${alpha('#D4AF37', 0.4)}`,
                }}
              >
                <SmartToyIcon sx={{ fontSize: '14px', color: '#D4AF37' }} />
              </Box>
              <Typography variant="caption" sx={{ color: '#D4AF37', fontWeight: 'medium' }}>
                {typingMessage}
              </Typography>
            </TypingIndicator>
          )}

          <Box ref={messagesEndRef} />

          {/* Escalation Banner */}
          <Collapse in={escalationStatus !== null}>
            <Alert
              severity="warning"
              sx={{
                mt: 2,
                backgroundColor: alpha('#FF9500', 0.2),
                color: '#FF9500',
                border: `1px solid ${alpha('#FF9500', 0.4)}`,
                borderRadius: '12px',
                '& .MuiAlert-icon': {
                  color: '#FF9500',
                },
                boxShadow: `0 4px 12px ${alpha('#FF9500', 0.2)}`,
              }}
            >
              {escalationStatus?.message || 'Connecting to live agent...'}
            </Alert>
          </Collapse>
        </MessagesContainer>

        <Box
          sx={{
            borderTop: `2px solid ${alpha('#D4AF37', 0.2)}`,
            padding: '16px 20px',
            background: `linear-gradient(180deg, ${alpha('#121212', 1)} 0%, ${alpha('#1a1a1a', 1)} 100%)`,
            position: 'relative',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '2px',
              background: `linear-gradient(90deg, transparent, ${alpha('#D4AF37', 0.6)}, transparent)`,
            },
          }}
        >
          <ChatInput
            onSend={handleSendMessage}
            disabled={isTyping || escalationStatus?.status === 'escalating'}
          />
          {/* Collapse Button */}
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
            <IconButton
              onClick={handleToggleCollapse}
              sx={{
                color: '#D4AF37',
                backgroundColor: alpha('#D4AF37', 0.1),
                borderRadius: '8px',
                width: '100%',
                py: 0.5,
                '&:hover': {
                  backgroundColor: alpha('#D4AF37', 0.2),
                  color: '#E8C547',
                },
                transition: 'all 0.2s ease',
              }}
            >
              <ExpandMoreIcon sx={{ fontSize: '24px' }} />
            </IconButton>
          </Box>
        </Box>
      </Box>
    </ChatPanel>
  );
};

export default AIChatPanel;
