import { Autocomplete } from "@mantine/core"
import { Search } from "lucide-react"

type SearchBarProps = {
  placeholder: string
  onChange: (value: string) => void
  value: string
  onSubmit: (value: string) => void
}

const SearchBar = ({
  placeholder,
  onChange,
  value,
  onSubmit,
}: SearchBarProps) => {
  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter" && onSubmit) {
      event.preventDefault()
      onSubmit(value)
    }
  }

  return (
    <Autocomplete
      placeholder={placeholder}
      onChange={onChange}
      value={value}
      leftSection={<Search size={20} />}
      data={JSON.parse(localStorage.getItem("history") || "[]")}
      className="w-[600px]"
      radius="xl"
      onKeyDown={handleKeyDown}
    />
  )
}

export default SearchBar
