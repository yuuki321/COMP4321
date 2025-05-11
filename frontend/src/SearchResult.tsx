import { type SearchResultType } from "./types"
import { Button } from "@mantine/core"
import Badge from "./Badge"
import { Anchor } from "@mantine/core"
import KeywordBadge from "./KeywordBadge"

const SearchResult = ({ result }: { result: SearchResultType }) => {
  return (
    <div className="flex flex-row items-center">
      <div className="flex flex-col w-[120px] gap-[16px] items-center">
        <span className="text-[12px]">Score</span>
        <span className="text-[24px]">{result.score}</span>
      </div>

      <div className="flex flex-col px-[40px] py-[20px] gap-[8px] border-l-[1px] border-[#888888] w-[924px]">
        <div className="flex flex-row gap-[20px] flex-1">
          <span className="text-[20px] text-[#228BE6] text-wrap">
            {result.title}
          </span>
          <Button variant="light">Get Similar Pages</Button>
        </div>

        <Anchor href={result.url} target="_blank" fz={14}>
          {result.url}
        </Anchor>

        <div className="flex flex-row gap-[20px]">
          <Badge label="Last modification date" text={result.lastModified} />
          <Badge label="Size of page" text={result.size.toString()} />
        </div>

        <div className="flex flex-row gap-[20px]">
          {result.keywords.map((keyword, index) => (
            <KeywordBadge key={index} keyword={keyword} />
          ))}
        </div>

        <div className="flex flex-row gap-[20px] pt-[12px]">
          <div className="flex flex-col gap-[8px] w-[412px]">
            <div className="w-full border-b-[1px] border-[#888888]">
              <span className="text-[14px]">Parent link(s)</span>
            </div>
            {result.parentLinks.map((link, index) => (
              <Anchor key={index} href={link} target="_blank" fz={14}>
                {link}
              </Anchor>
            ))}
          </div>
          <div className="flex flex-col gap-[8px] w-[412px]">
            <div className="w-full border-b-[1px] border-[#888888]">
              <span className="text-[14px]">Child link(s)</span>
            </div>
            {result.childLinks.map((link, index) => (
              <Anchor key={index} href={link} target="_blank" fz={14}>
                {link}
              </Anchor>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default SearchResult
