import { X } from "lucide-react"

type HistoryItemProps = {
  text: string
  onDelete: (text: string) => void
  onSearch: (text: string) => void
}

const HistoryItem = ({ text, onDelete, onSearch }: HistoryItemProps) => {
  return (
    <div className="flex flex-row w-[400px] items-center py-[28px] border-b-[1px] border-[#888888] justify-between">
      <span
        className="font-bold text-[16px] cursor-pointer"
        onClick={() => onSearch(text)}
      >
        {text}
      </span>
      <X onClick={() => onDelete(text)} className="cursor-pointer" />
    </div>
  )
}

export default HistoryItem
