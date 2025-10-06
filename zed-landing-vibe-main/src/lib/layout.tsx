import { createContext, useContext, useEffect, useMemo, useState } from "react";

type LayoutCtx={attached:boolean;width:number;setAttached:(v:boolean)=>void;setWidth:(w:number)=>void};
const Ctx=createContext<LayoutCtx>({attached:false,width:0,setAttached:()=>{},setWidth:()=>{}});

export function LayoutProvider({children}:{children:any}){
  const [attached,setAttached]=useState<boolean>(()=>localStorage.getItem('agent-assistant-attached')==='true');
  const [width,setWidth]=useState<number>(()=>parseInt(localStorage.getItem('agent-assistant-width')||'400')||400);
  useEffect(()=>{localStorage.setItem('agent-assistant-attached',String(attached));},[attached]);
  useEffect(()=>{localStorage.setItem('agent-assistant-width',String(width));},[width]);
  const v=useMemo(()=>({attached,width,setAttached,setWidth}),[attached,width]);
  return <Ctx.Provider value={v}>{children}</Ctx.Provider>;
}

export function useLayout(){return useContext(Ctx)}

export function LayoutContainer({children}:{children:any}){
  const {attached,width}=useLayout();
  return <div style={{paddingRight:attached?`${width}px`:undefined,transition:'padding-right .3s ease-in-out'}}>{children}</div>;
}
