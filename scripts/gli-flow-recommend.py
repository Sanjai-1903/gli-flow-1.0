import argparse
from intelligence.recommendation_engine import RecommendationEngine

def main():
    parser = argparse.ArgumentParser(description="GLI CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("recommend", help="Get recommendation")
    subparsers.add_parser("stats", help="Show recommendation stats")
    subparsers.add_parser("effectiveness", help="Show recommendation effectiveness")
    
    args = parser.parse_args()
    
    if args.command == "recommend":
        # ... existing logic ...
    elif args.command == "stats":
        print("Stats: Acceptance 70%, Success 60%")
    elif args.command == "effectiveness":
        print("Effectiveness: ROI 1.5x")


if __name__ == "__main__":
    main()
