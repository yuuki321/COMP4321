import "@mantine/core/styles.css"
import { MantineProvider, createTheme } from "@mantine/core"
import { Tabs } from "@mantine/core"
import Search from "./Search"
import History from "./History"
import Keywords from "./Keywords"
import { Routes, Route, useLocation, useNavigate } from "react-router-dom"

// Create a custom theme with fullscreen app configuration
const theme = createTheme({
  components: {
    MantineProvider: {
      defaultProps: {
        withGlobalStyles: true,
        withNormalizeCSS: true,
      },
    },
    Anchor: {
      styles: {
        root: {
          color: "black",
        },
      },
    },
    Spoiler: {
      styles: {
        control: {
          color: "#228BE6",
        },
      },
    },
  },
})

function App() {
  const location = useLocation()
  const navigate = useNavigate()

  const getCurrentTab = () => {
    const path = location.pathname
    if (path === "/history") return "history"
    if (path === "/keywords") return "keywords"
    return "search"
  }

  return (
    <MantineProvider theme={theme}>
      <Tabs
        defaultValue="search"
        className="pt-[60px]"
        value={getCurrentTab()}
        onChange={(value) => {
          if (value === "search") {
            navigate("/")
            return
          }
          navigate(`/${value}`)
        }}
      >
        <Tabs.List justify="center">
          <Tabs.Tab value="search">Search</Tabs.Tab>
          <Tabs.Tab value="history">History</Tabs.Tab>
          <Tabs.Tab value="keywords">Keywords</Tabs.Tab>
        </Tabs.List>

        <Routes>
          <Route path="/" element={<Search />} />
          <Route path="/history" element={<History />} />
          <Route path="/keywords" element={<Keywords />} />
        </Routes>
      </Tabs>
    </MantineProvider>
  )
}

export default App
