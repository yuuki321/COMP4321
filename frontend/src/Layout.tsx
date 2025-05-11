type LayoutProps = {
  children: React.ReactNode
}

const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="flex flex-col min-h-screen w-full py-[40px] gap-[40px] items-center bg-white">
      {children}
    </div>
  )
}

export default Layout
