
import { Button } from "./ui/button"

const Header = () => {
  return (
    <header className="h-16 w-full flex items-center px-4 border-b">
      <div className="flex items-center justify-between w-full">
        <h1 className="text-xl font-bold text-blue-600">Trip Master</h1>
        <div className="flex space-x-2">
          <Button variant="ghost" className="text-sm text-gray-700 hover:bg-gray-100" onClick={() => alert("功能开发中")}>
            地点
          </Button>
          <Button variant="ghost" className="text-sm text-gray-700 hover:bg-gray-100" onClick={() => alert("功能开发中")}>
            日期
          </Button>
          <Button variant="ghost" className="text-sm text-gray-700 hover:bg-gray-100" onClick={() => alert("功能开发中")}>
            几位旅客
          </Button>
          <Button variant="ghost" className="text-sm text-gray-700 hover:bg-gray-100" onClick={() => alert("功能开发中")}>
            预算
          </Button>
        </div>
        <div></div>
      </div>
      {/* TODO: Integrate backend API */}
    </header>
  )
}

export default Header
