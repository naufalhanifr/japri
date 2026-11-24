import type { ButtonHTMLAttributes } from 'react'
import { Link, type LinkProps } from 'react-router-dom'

type Variant = 'primary' | 'secondary' | 'ghost'

const classes = (variant: Variant, extra?: string) => ['btn', `btn--${variant}`, extra].filter(Boolean).join(' ')

export function Button({
  variant = 'secondary',
  className,
  type = 'button',
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return <button type={type} className={classes(variant, className)} {...rest} />
}

export function ButtonLink({ variant = 'secondary', className, ...rest }: LinkProps & { variant?: Variant }) {
  return <Link className={classes(variant, className)} {...rest} />
}
