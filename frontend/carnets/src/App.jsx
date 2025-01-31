import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import IDPhotoProcessor from './photopross'
function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <IDPhotoProcessor />
    </>
  )
}

export default App
