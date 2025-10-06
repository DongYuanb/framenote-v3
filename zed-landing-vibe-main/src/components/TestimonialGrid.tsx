import { Star } from "lucide-react";

export function TestimonialGrid() {
  const testimonials = [
    {
      name: "张老师",
      role: "大学讲师",
      content: "FrameNote让我的备课效率提升了3倍，PPT提取非常精准！",
      rating: 5
    },
    {
      name: "李教授",
      role: "教育专家",
      content: "AI生成的讲义质量很高，学生反馈很好。",
      rating: 5
    },
    {
      name: "王老师",
      role: "中学教师",
      content: "界面简洁，操作简单，非常适合日常教学使用。",
      rating: 5
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {testimonials.map((testimonial, index) => (
        <div key={index} className="bg-card rounded-lg border p-6">
          <div className="flex items-center gap-1 mb-4">
            {[...Array(testimonial.rating)].map((_, i) => (
              <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
            ))}
          </div>
          <p className="text-muted-foreground mb-4">"{testimonial.content}"</p>
          <div>
            <p className="font-medium">{testimonial.name}</p>
            <p className="text-sm text-muted-foreground">{testimonial.role}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
