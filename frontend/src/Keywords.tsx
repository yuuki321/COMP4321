import Layout from "./Layout"
import { useEffect, useState } from "react"
import KeywordSection from "./KeywordSection"
import KeywordButton from "./KeywordButton"
import { Button } from "@mantine/core"
import { useNavigate } from "react-router-dom"

const alphabet = "abcdefghijklmnopqrstuvwxyz"

const groupByFirstLetter = (keywords: string[]): Record<string, string[]> => {
  return keywords.reduce((acc, keyword) => {
    const firstLetter = keyword[0].toLowerCase()
    if (!acc[firstLetter]) {
      acc[firstLetter] = []
    }
    acc[firstLetter].push(keyword)
    return acc
  }, {} as Record<string, string[]>)
}

const Keywords = () => {
  const [keywords, setKeywords] = useState<Record<string, string[]>>({}) // Grouped by starting letter
  const [keywordCount, setKeywordCount] = useState<number>(0)
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([])
  const navigate = useNavigate()

  useEffect(() => {
    try {
      fetch("http://localhost:5000/keywords")
        .then((res) => res.json())
        .then((data) => {
          setKeywordCount(data.length)
          setKeywords(groupByFirstLetter(data))
        })
    } catch (error) {
      console.error("Error fetching keywords:", error)
    }
  }, [])

  const handleKeywordClick = (keyword: string) => {
    if (selectedKeywords.includes(keyword)) {
      setSelectedKeywords(selectedKeywords.filter((k) => k !== keyword))
    } else {
      setSelectedKeywords([...selectedKeywords, keyword])
    }
  }

  const handleSearch = () => {
    if (selectedKeywords.length === 0) return
    const searchQuery = selectedKeywords.join(" ")
    navigate(`/?q=${encodeURIComponent(searchQuery)}`)
  }

  return (
    <Layout>
      <div className="flex flex-col gap-[12px] items-center">
        <span className="text-[20px]">
          Select keywords below to search for documents
        </span>
        <span className="text-[14px]">Indexed {keywordCount} keywords</span>
      </div>

      {selectedKeywords.length > 0 ? (
        <div className="flex flex-row w-[600px] items-center justify-between">
          <div className="flex flex-row gap-[12px] items-center">
            <span className="text-[14px]">Selected:</span>
            {selectedKeywords.map((keyword) => (
              <KeywordButton
                key={keyword}
                keyword={keyword}
                isSelected={selectedKeywords.includes(keyword)}
                onClick={handleKeywordClick}
              />
            ))}
          </div>
          <Button variant="filled" onClick={handleSearch}>
            Search
          </Button>
        </div>
      ) : (
        <span>
          No keywords selected, please click on a keyword to get started
        </span>
      )}

      {alphabet.split("").map((letter) => {
        const keywordsForLetter = keywords[letter] || []
        if (keywordsForLetter.length === 0) return null // Skip empty sections
        return (
          <KeywordSection
            key={letter}
            startingLetter={letter.toUpperCase()}
            keywords={keywordsForLetter}
            handleKeywordClick={handleKeywordClick}
            selectedKeywords={selectedKeywords}
          />
        )
      })}
    </Layout>
  )
}

export default Keywords
