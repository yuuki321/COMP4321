import { type Keyword } from "./types"

type KeywordBadgeProps = {
  keyword: Keyword
}

const KeywordBadge = ({ keyword }: KeywordBadgeProps) => {
  return (
    <div className="flex px-[12px] py[4px] rounded-[20px] border-[#228BE6] border-[1px]">
      <span className="text-[#228BE6] text-[14px]">{`${keyword.keyword} | ${keyword.count}`}</span>
    </div>
  )
}

export default KeywordBadge
