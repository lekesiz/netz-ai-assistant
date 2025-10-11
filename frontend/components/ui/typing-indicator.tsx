'use client'

import { motion } from 'framer-motion'

export function TypingIndicator() {
  return (
    <div className="flex items-center space-x-2 p-4 rounded-lg bg-muted w-fit">
      <div className="flex space-x-1">
        {[0, 1, 2].map((index) => (
          <motion.div
            key={index}
            className="w-2 h-2 bg-primary/60 rounded-full"
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.5, 1, 0.5]
            }}
            transition={{
              duration: 1,
              delay: index * 0.2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        ))}
      </div>
      <span className="text-sm text-muted-foreground">AI yazıyor...</span>
    </div>
  )
}