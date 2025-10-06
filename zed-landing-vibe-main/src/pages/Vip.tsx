import { useAuth } from "@/lib/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useEffect, useState } from "react";
import { getMembershipPlans, upgradeMembership } from "@/lib/api";

type Plan = { id:string; name:string; price:number; currency:string; duration_days:number; benefits:string[] };

export default function VipPage() {
  const { membership, user, token, refresh } = useAuth();
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState<string | null>(null);

  useEffect(() => {
    getMembershipPlans().then(res=> setPlans(res.plans||[])).finally(()=> setLoading(false));
  }, []);

  if (!user) {
    return (
      <div className="container mx-auto py-10">
        <Card>
          <CardHeader>
            <CardTitle>会员中心</CardTitle>
            <CardDescription>请先登录</CardDescription>
          </CardHeader>
          <CardContent>
            <a href="/login" className="underline">立即登录</a>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-10">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map((p)=> (
          <Card key={p.id}>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{p.name}</span>
                <Badge variant="secondary">{p.duration_days}天</Badge>
              </CardTitle>
              <CardDescription>
                <span className="text-2xl font-semibold mr-1">¥{p.price}</span>
                <span className="text-xs text-muted-foreground">含 {p.benefits.length} 项权益</span>
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="list-disc pl-5 text-sm text-muted-foreground space-y-1">
                {p.benefits.map((b,i)=>(<li key={i}>{b}</li>))}
              </ul>
              <Button className="mt-4 w-full" disabled={!token || submitting===p.id} onClick={async()=>{
                if(!token) return;
                setSubmitting(p.id);
                try{
                  await upgradeMembership(token, p.id);
                  await refresh();
                }finally{setSubmitting(null)}
              }}>{submitting===p.id? '开通中...':'立即开通'}</Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}


