import "@mantine/core/styles.css"
import { MantineProvider, createTheme } from "@mantine/core"
import { Tabs } from "@mantine/core"
import "./index.css"
import Search from "./Search"

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
  },
})

function App() {
  return (
    <MantineProvider theme={theme}>
      <Tabs defaultValue="search" className="pt-[60px]">
        <Tabs.List justify="center">
          <Tabs.Tab value="search">Search</Tabs.Tab>
          <Tabs.Tab value="history">History</Tabs.Tab>
          <Tabs.Tab value="keywords">Keywords</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="search">
          <Search />
        </Tabs.Panel>
        <Tabs.Panel value="history">History content</Tabs.Panel>
        <Tabs.Panel value="keywords">Keywords content</Tabs.Panel>
      </Tabs>
    </MantineProvider>
  )
}

export default App
