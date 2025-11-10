
import { Button } from "./ui/button"
import { useAuthStore } from "@/store/authStore.tsx"
import { toast } from "react-hot-toast"

const Header = () => {
  const { user, openAuthModal } = useAuthStore();

  // 检查用户是否已登录，如果未登录则提示并打开登录框
  const checkAuthAndExecute = (callback: () => void, message: string) => {
    if (user) {
      callback();
    } else {
      toast.error(message);
      openAuthModal();
    }
  };

  return (
    <header className="h-16 w-full flex items-center px-4 border-b">
      <div className="flex items-center justify-between w-full">
        <h1 className="text-xl font-bold text-blue-600">Trip Master</h1>
        <div className="flex space-x-2">
          <Button variant="ghost" className="text-sm text-gray-700 hover:bg-gray-100" onClick={() => checkAuthAndExecute(() => alert("功能开发中"), "请先登录后再选择地点")}>
            地点
          </Button>
          <Button variant="ghost" className="text-sm text-gray-700 hover:bg-gray-100" onClick={() => checkAuthAndExecute(() => alert("功能开发中"), "请先登录后再选择日期")}>
            日期
          </Button>
          <Button variant="ghost" className="text-sm text-gray-700 hover:bg-gray-100" onClick={() => checkAuthAndExecute(() => alert("功能开发中"), "请先登录后再选择旅客人数")}>
            几位旅客
          </Button>
          <Button variant="ghost" className="text-sm text-gray-700 hover:bg-gray-100" onClick={() => checkAuthAndExecute(() => alert("功能开发中"), "请先登录后再设置预算")}>
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
