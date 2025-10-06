import React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { MessageCircle, Send } from 'lucide-react';

interface AgentAssistantProps {
  attached: boolean;
  setAttached: (attached: boolean) => void;
}

export function AgentAssistant({ attached, setAttached }: AgentAssistantProps) {
  return (
    <div className="w-full max-w-md">
      <div className="border rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">AI 助手</h3>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAttached(!attached)}
          >
            {attached ? '分离' : '附加'}
          </Button>
        </div>
        
        <div className="space-y-3">
          <div className="p-3 bg-muted rounded-lg">
            <p className="text-sm">你好！我是你的AI助手，有什么可以帮助你的吗？</p>
          </div>
          
          <div className="flex space-x-2">
            <Input
              placeholder="输入你的问题..."
              className="flex-1"
            />
            <Button size="sm">
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
