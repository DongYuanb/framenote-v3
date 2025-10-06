import { useState, useEffect, useRef, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FileText, Loader2, RefreshCw, ChevronDown, ChevronUp } from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { getStreamSummaryUrl } from "@/lib/api";

interface Props{taskId:string}

// 智能摘要组件（直接请求流式端点）
export function StreamingSummary({taskId}:Props){
  const [isOpen,setIsOpen]=useState(true);
  const [txt,setTxt]=useState("");
  const [ing,setIng]=useState(false);
  const [started,setStarted]=useState(false);
  const [err,setErr]=useState<string|null>(null);
  const [waiting,setWaiting]=useState(false); // ASR 未就绪
  const acRef=useRef<AbortController|null>(null);
  const tRef=useRef<number|undefined>(undefined);

  const start=useCallback(async()=>{
    if(ing||!taskId)return;
    setIng(true);setStarted(true);setWaiting(false);setErr(null);setTxt("");
    acRef.current=new AbortController();
    try{
      const r=await fetch(getStreamSummaryUrl(taskId),{signal:acRef.current.signal});
      if(r.status===404){setWaiting(true);setIng(false);return;} // ASR 未就绪
      if(!r.ok) throw new Error(`HTTP ${r.status}: ${r.statusText}`);
      const rd=r.body?.getReader(); if(!rd) throw new Error("无法获取响应流");
      const dec=new TextDecoder(); let buf="";
      while(true){const {done,value}=await rd.read(); if(done)break; buf+=dec.decode(value,{stream:true}); setTxt(buf);}
    }catch(e:any){ if(e.name!=="AbortError") setErr(e.message||"生成摘要时发生错误"); }
    finally{ setIng(false);}
  },[ing,taskId]);

  const stop=()=>{acRef.current?.abort();setIng(false);}
  const regen=()=>{setTxt("");setStarted(false);setErr(null);start();}

  useEffect(()=>()=>{acRef.current?.abort(); if(tRef.current) window.clearTimeout(tRef.current);},[]);
  useEffect(()=>{ if(!started&&!ing) start(); },[started,ing,start]);
  useEffect(()=>{ if(waiting&&!ing&&!txt){ tRef.current=window.setTimeout(()=>start(),1500);} return ()=>{ if(tRef.current) window.clearTimeout(tRef.current);} },[waiting,ing,txt,start]);

  return(
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <Card>
        <CollapsibleTrigger asChild>
          <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                <CardTitle className="text-lg">智能摘要</CardTitle>
                {ing&&(<Badge variant="default" className="animate-pulse"><Loader2 className="w-3 h-3 mr-1 animate-spin"/>生成中</Badge>)}
                {started&&!ing&&txt&&(<Badge variant="secondary">已完成</Badge>)}
                {waiting&&(<Badge variant="outline">等待转录完成</Badge>)}
              </div>
              <Button variant="ghost" size="sm">{isOpen?<ChevronUp className="w-4 h-4"/>:<ChevronDown className="w-4 h-4"/>}</Button>
            </div>
          </CardHeader>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <CardContent className="pt-0">


            {ing&&(
              <div className="text-center py-6"><Loader2 className="w-5 h-5 mx-auto mb-2 animate-spin text-primary"/>
                <p className="text-muted-foreground text-sm">正在生成智能摘要，请稍候...</p>
              </div>
            )}

            {started&&(
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  {ing&&(<Button variant="outline" size="sm" onClick={stop}>停止生成</Button>)}
                  {!ing&&txt&&(<Button variant="outline" size="sm" onClick={regen}><RefreshCw className="w-4 h-4 mr-2"/>重新生成</Button>)}
                  {!ing&&!txt&&!waiting&&(<Button variant="outline" size="sm" onClick={start}>开始生成</Button>)}
                </div>
                <div className="min-h-[80px] max-h-[320px] overflow-y-auto">
                  {err?(
                    <div className="text-red-500 p-4 bg-red-50 rounded-md"><p className="font-medium">生成失败</p>
                      <p className="text-sm mt-1">{err}</p></div>
                  ):(
                    <div className="prose prose-sm max-w-none"><div className="whitespace-pre-wrap text-sm leading-relaxed">{txt}{ing&&(<span className="inline-block w-2 h-4 bg-primary animate-pulse ml-1"/>)}</div></div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </CollapsibleContent>
      </Card>
    </Collapsible>
  );
}
