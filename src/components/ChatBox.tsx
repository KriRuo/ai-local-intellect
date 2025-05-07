
import { useState } from "react";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { SendIcon } from "lucide-react";
import { useAppStore, ChatMessage } from "@/lib/store";
import { sendChatMessage } from "@/lib/api";
import { v4 as uuidv4 } from "uuid";

export function ChatBox() {
  const [input, setInput] = useState("");
  const { 
    chatMessages, 
    addChatMessage, 
    isLoadingChat, 
    setIsLoadingChat, 
    setChatError 
  } = useAppStore();

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || isLoadingChat) return;
    
    const userMessage: ChatMessage = {
      id: uuidv4(),
      content: input,
      role: "user",
      timestamp: new Date(),
    };
    
    addChatMessage(userMessage);
    setInput("");
    setIsLoadingChat(true);
    
    try {
      const response = await sendChatMessage(input);
      
      const assistantMessage: ChatMessage = {
        id: uuidv4(),
        content: response,
        role: "assistant",
        timestamp: new Date(),
      };
      
      addChatMessage(assistantMessage);
    } catch (error) {
      setChatError(error instanceof Error ? error.message : "Failed to send message");
      console.error("Chat error:", error);
    } finally {
      setIsLoadingChat(false);
    }
  };

  return (
    <Card className="w-full h-full flex flex-col">
      <CardHeader className="px-4 pt-4 pb-0">
        <CardTitle className="text-xl">AI Assistant</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 p-4 overflow-hidden">
        <ScrollArea className="h-[calc(100%-2rem)] pr-4">
          {chatMessages.length === 0 ? (
            <div className="h-full flex items-center justify-center text-center text-muted-foreground p-4">
              <p>
                Ask me questions about the latest AI news.<br />
                <span className="text-sm opacity-70">
                  Try "What happened in AI today?" or "Summarize recent OpenAI announcements"
                </span>
              </p>
            </div>
          ) : (
            <div className="space-y-4 py-2">
              {chatMessages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      message.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted"
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
          {isLoadingChat && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-lg p-3 bg-muted">
                <div className="flex space-x-2">
                  <div className="h-2 w-2 rounded-full bg-muted-foreground animate-pulse-slow"></div>
                  <div className="h-2 w-2 rounded-full bg-muted-foreground animate-pulse-slow [animation-delay:0.2s]"></div>
                  <div className="h-2 w-2 rounded-full bg-muted-foreground animate-pulse-slow [animation-delay:0.4s]"></div>
                </div>
              </div>
            </div>
          )}
        </ScrollArea>
      </CardContent>
      <CardFooter className="p-4 pt-0">
        <form onSubmit={handleSendMessage} className="flex w-full gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about recent AI news..."
            disabled={isLoadingChat}
            className="flex-1"
          />
          <Button type="submit" size="icon" disabled={isLoadingChat || !input.trim()}>
            <SendIcon className="h-4 w-4" />
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
}
