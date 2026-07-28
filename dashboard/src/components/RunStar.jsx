import { Star } from "lucide-react"

export default function RunStar({ isImportant, onClick }) {
  return (
    <button
      onClick={(e) => { e.stopPropagation(); onClick(!isImportant); }}
      className={`cursor-pointer transition-colors ${
        isImportant ? "text-[#F59E0B]" : "text-[#D1D5DB] hover:text-[#F59E0B]"
      }`}
      title="Help teach GLI-FLOW which runs are important"
    >
      <Star size={16} fill={isImportant ? "#F59E0B" : "none"} />
    </button>
  )
}
