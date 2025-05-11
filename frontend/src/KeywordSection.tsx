import KeywordButton from "./KeywordButton"
import { Spoiler } from "@mantine/core"

type KeywordSectionProps = {
  startingLetter: string
  keywords: string[]
  selectedKeywords: string[]
  handleKeywordClick: (keyword: string) => void
}

const KeywordSection = ({
  startingLetter,
  keywords,
  selectedKeywords,
  handleKeywordClick,
}: KeywordSectionProps) => {
  return (
    <div className="flex flex-col gap-[20px] w-[800px]">
      <div className="px-[20px] py-[8px] text-[#888888] border-[#888888] border-b-[1px] text-[32px]">
        {startingLetter}
      </div>
      <Spoiler maxHeight={200} showLabel="Show more" hideLabel="Hide">
        <div className="flex flex-wrap gap-[8px]">
          {keywords.map((keyword) => (
            <KeywordButton
              key={keyword}
              keyword={keyword}
              isSelected={selectedKeywords.includes(keyword)}
              onClick={handleKeywordClick}
            />
          ))}
        </div>
      </Spoiler>
    </div>
  )
}

export default KeywordSection
