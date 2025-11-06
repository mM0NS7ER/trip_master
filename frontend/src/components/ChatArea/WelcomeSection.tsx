
const WelcomeSection = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <h1 className="text-xl text-blue-600 mb-2">今天想去哪儿？</h1>
      <p className="text-sm text-gray-500 mb-4 text-center max-w-md">
        嘿，我来帮你规划你的旅行。任何旅行相关的问题都可以问我。
      </p>
      <button 
        className="text-blue-500 text-sm hover:underline" 
        onClick={() => alert("我可以帮你规划行程、推荐景点、预订酒店等旅行相关问题！")}
      >
        我可以向Mindtrip询问什么？
      </button>
    </div>
  )
}

export default WelcomeSection
