export type Keyword = {
  keyword: string
  count: number
}

export type SearchResultType = {
  title: string
  url: string
  lastModified: string
  size: number
  parentLinks: string[]
  childLinks: string[]
  score: number // rounded to 1 decimal place
  keywords: Keyword[]
  id: number
}
