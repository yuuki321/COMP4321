type BadgeProps = {
  label: string
  text: string
}

const Badge = ({ label, text }: BadgeProps) => {
  return (
    <div className="flex flex-row px-[12px] py[4px] gap-[8px] bg-[#228BE6] rounded-[20px] items-center">
      <span className="text-[12px] text-white">{label}</span>
      <span className="text-[14px] text-white">{text}</span>
    </div>
  )
}

export default Badge
