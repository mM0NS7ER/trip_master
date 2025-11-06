
import { useEffect, useRef } from "react"

declare global {
  interface Window {
    AMap: any
  }
}

const MapArea = () => {
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<any>(null)

  useEffect(() => {
    // 初始化地图
    if (mapContainerRef.current && !mapRef.current && window.AMap) {
      mapRef.current = new window.AMap.Map(mapContainerRef.current, {
        zoom: 15,
        center: [116.397428, 39.90923], // 北京天安门
        mapStyle: "amap://styles/light" // 浅色主题
      })

      // 添加标记点
      const marker = new window.AMap.Marker({
        position: [116.397428, 39.90923],
        title: "北京天安门"
      })
      mapRef.current.add(marker)

      // 添加另一个标记点
      const marker2 = new window.AMap.Marker({
        position: [116.407428, 39.91923],
        title: "故宫博物院"
      })
      mapRef.current.add(marker2)
    }

    return () => {
      // 清理地图实例
      if (mapRef.current) {
        mapRef.current.destroy()
        mapRef.current = null
      }
    }
  }, [])

  const handleSearch = () => {
    // 模拟搜索功能，随机改变地图中心点
    if (mapRef.current) {
      const randomLng = 116.397428 + (Math.random() - 0.5) * 0.1
      const randomLat = 39.90923 + (Math.random() - 0.5) * 0.1
      mapRef.current.setCenter([randomLng, randomLat])
    }
    // TODO: Integrate backend for POI search
  }

  return (
    <div className="relative h-full">
      {/* 顶部搜索栏 */}
      <div className="absolute top-4 left-4 right-4 z-10 bg-white rounded-lg shadow-md p-3 flex items-center space-x-2">
        <input
          type="text"
          placeholder="出发地"
          className="border rounded px-2 py-1 flex-1"
        />
        <input
          type="text"
          placeholder="目的地"
          className="border rounded px-2 py-1 flex-1"
        />
        <button
          onClick={handleSearch}
          className="bg-blue-500 text-white px-4 py-1 rounded hover:bg-blue-600"
        >
          搜索
        </button>
      </div>

      {/* 地图容器 */}
      <div id="map-container" ref={mapContainerRef} className="w-full h-full"></div>
    </div>
  )
}

export default MapArea
