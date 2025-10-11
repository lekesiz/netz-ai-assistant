'use client'

import { motion } from 'framer-motion'

export function LoadingDots() {
  return (
    <div className="flex space-x-1">
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          className="w-2 h-2 bg-primary rounded-full"
          animate={{
            y: [0, -10, 0],
            opacity: [0.5, 1, 0.5]
          }}
          transition={{
            duration: 1,
            delay: index * 0.15,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      ))}
    </div>
  )
}