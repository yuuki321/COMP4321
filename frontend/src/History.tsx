import Layout from "./Layout"
import HistoryItem from "./HistoryItem"
import { useNavigate } from "react-router-dom"
import { useState, useEffect } from "react"

const History = () => {
  const navigate = useNavigate()
  const [historyItems, setHistoryItems] = useState<string[]>([])

  useEffect(() => {
    const storedHistory = JSON.parse(localStorage.getItem("history") || "[]")
    setHistoryItems(storedHistory)
  }, [])

  const handleDelete = (text: string) => {
    const updatedHistory = historyItems.filter((item) => item !== text)
    localStorage.setItem("history", JSON.stringify(updatedHistory))
    setHistoryItems(updatedHistory)
  }

  const handleSearch = (text: string) => {
    navigate(`/?q=${encodeURIComponent(text)}`)
  }

  return (
    <Layout>
      <span className="text-[20px]">Search history</span>
      <div>
        {historyItems.map((item, index) => (
          <HistoryItem
            key={index}
            text={item}
            onDelete={handleDelete}
            onSearch={handleSearch}
          />
        ))}
        {historyItems.length === 0 && <span>No search history available.</span>}
      </div>
    </Layout>
  )
}

export default History
