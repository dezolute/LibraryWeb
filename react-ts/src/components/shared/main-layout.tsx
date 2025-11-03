import { ConfigProvider } from "antd";
import { Layout, Divider } from "antd";

const { Header, Content, Footer } = Layout

const MainLayout = ({ children }) => {
  return (
    <>
      <ConfigProvider
        theme={{
          components: {
            Layout: {
              headerBg: "#00B96B",
              headerColor: "white"
            }
          }
        }}
      >
        <Layout className="min-h-screen md:px-0 lg:px-24 flex">
          <Header className="text-2xl rounded-b-3xl max-h-20 flex items-center justify-between">
            <div className="font-bold flex flex-row items-center gap-3">
              <img className="size-[45px]" src="/LibraryWeb.svg" alt="LibraryLogo" />
              LibraryWeb
              <Divider type="vertical" className="bg-white min-h-[45px]" /> 
            </div>
            <div className=" font-bold flex flex-row items-center gap-3">
              Account
              <img className="size-[45px] rounded-full" src="/Krol.jpg" alt="" />
            </div>
          </Header>
          <Content>{children}</Content>
          <Footer className="text-center">
            <span className="text-[1.05rem]">dezolute@LibraryWeb.com</span>
          </Footer>
        </Layout>
      </ConfigProvider>
    </>
  )
}

export default MainLayout