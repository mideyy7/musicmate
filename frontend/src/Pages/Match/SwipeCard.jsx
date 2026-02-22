import { motion, useMotionValue, useTransform } from "framer-motion";

export default function SwipeCard({ children, onSwipedLeft, onSwipedRight }) {
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-10, 10]);
  const opacity = useTransform(x, [-200, 0, 200], [0, 1, 0]);

  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      style={{ x, rotate, opacity, touchAction: "pan-y" }}
      whileTap={{ scale: 0.98 }}
      onDragEnd={(event, info) => {
        const offset = info.offset.x;
        const velocity = info.velocity.x;

        if (offset > 120 || velocity > 600) onSwipedRight?.();
        else if (offset < -120 || velocity < -600) onSwipedLeft?.();
      }}
      animate={{ x: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
    >
      {children}
    </motion.div>
  );
}