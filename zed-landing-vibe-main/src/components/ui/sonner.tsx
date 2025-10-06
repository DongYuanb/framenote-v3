import * as React from "react"

import { toast } from "sonner"

type ToasterProps = React.ComponentProps<typeof toast>

const Toaster = ({ ...props }: ToasterProps) => {
  return <toast.Toaster {...props} />
}

export { Toaster }