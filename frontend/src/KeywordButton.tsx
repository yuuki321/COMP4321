type KeywordSectionProps = {
  keyword: string
  isSelected: boolean
  onClick: (keyword: string) => void
}

const KeywordButton = ({
  keyword,
  isSelected,
  onClick,
}: KeywordSectionProps) => {
  return (
    <button
      onClick={() => onClick(keyword)}
      className={`px-[12px] py-[4px] text-[14px] rounded-[20px] ${
        isSelected
          ? "bg-[#228BE6] text-white"
          : "border-[#228BE6] border-[1px] text-[#228BE6] bg-white"
      }`}
    >
      {keyword}
    </button>
  )
}

export default KeywordButton
