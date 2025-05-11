import SearchBar from "./SearchBar"
import Layout from "./Layout"
import { useState, useEffect } from "react"
import { type SearchResultType } from "./types"
import SearchResult from "./SearchResult"
import { useLocation } from "react-router-dom"

const Search = () => {
  const [query, setQuery] = useState("")
  const [numberOfDocs, setNumberOfDocs] = useState(0)
  const [searchTime, setSearchTime] = useState(0) // in milliseconds
  const [searchResults, setSearchResults] = useState<SearchResultType[]>([])
  const [isGettingSimilarPages, setIsGettingSimilarPages] = useState(false) // True when the user clicks on "Get Similar Pages" button
  const [similarPagesTitle, setSimilarPagesTitle] = useState("") // Title of the page for which we are getting similar pages
  const [isSearching, setIsSearching] = useState(false) // True when the user is searching for a query
  const location = useLocation()

  useEffect(() => {
    setIsSearching(false)
  }, [])

  useEffect(() => {
    const searchParams = new URLSearchParams(location.search)
    const queryParam = searchParams.get("q")

    if (queryParam) {
      setQuery(queryParam)
      handleSearch(queryParam)
      console.log("Query param:", queryParam)
    }
  }, [location.search])

  const handleSearch = async (query: string, relatedId: number = -1) => {
    if (query.length === 0) {
      return
    }

    if (relatedId !== -1) {
      setIsGettingSimilarPages(true)
    } else {
      setIsGettingSimilarPages(false)
    }

    setIsSearching(true)

    try {
      const currentHistory = JSON.parse(localStorage.getItem("history") || "[]")
      if (!currentHistory.includes(query)) {
        const updatedHistory = [query, ...currentHistory]
        localStorage.setItem("history", JSON.stringify(updatedHistory))
      }

      const response = await fetch("http://localhost:5000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          searchbar: query,
          related_doc: relatedId,
        }),
      })
      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`)
      }
      const data = await response.json()
      //@ts-expect-error - Result type is expected to be correct
      data.results = data.results.filter((result) => result.id !== relatedId)
      setNumberOfDocs(data.results.length)
      setSearchTime(data.time_taken)
      setSearchResults(
        //@ts-expect-error - Result type is expected to be correct
        data.results.map((result) => ({
          title: result.title,
          url: result.url,
          lastModified: result.time,
          size: result.size,
          parentLinks: result.parent_links,
          childLinks: result.child_links,
          score: result.score,
          //@ts-expect-error - Keyword type is expected to be correct
          keywords: result.keywords.map((pair) => ({
            keyword: pair[0],
            count: pair[1],
          })),
          id: result.id,
        }))
      )
    } catch (error) {
      console.error("Error fetching search results:", error)
    }
  }

  return (
    <Layout>
      <div className="flex flex-col gap-[12px] items-center">
        <SearchBar
          placeholder="Search..."
          onChange={(value) => {
            setQuery(value)
          }}
          value={query}
          onSubmit={handleSearch}
        />
        {isSearching &&
          (searchResults.length > 0 ? (
            <span>
              Retrieved {numberOfDocs} document(s)
              {isGettingSimilarPages
                ? ` related to "${similarPagesTitle}"`
                : `for "${query}"`}{" "}
              in {searchTime}ms.
            </span>
          ) : (
            <span>No results found for "{query}"</span>
          ))}
      </div>

      {searchResults.map((result, index) => (
        <SearchResult
          key={index}
          result={result}
          isGettingSimilarPages={isGettingSimilarPages}
          getSimilarPages={(id: number, title: string) => {
            setSimilarPagesTitle(title)
            handleSearch(query, id)
          }}
        />
      ))}
    </Layout>
  )
}

export default Search
