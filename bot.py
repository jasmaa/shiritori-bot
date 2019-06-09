import praw
from shiritori import Game    

def process_comment(game, comment):
    """Descends and processes replies"""
    print(comment.body)
    print(game.last_word)

    with open("reply_ids.txt", "r") as f:
        reply_ids = set(f.read().split("\n"))

    if comment.id not in reply_ids:
        try:
            g = game.copy()
            g.add_word(comment.body)
            
        except Exception as error:

            # check if comment already replied to
            is_replied = False
            for c in comment.replies.list():
                if c.id in reply_ids:
                    is_replied = True
                    break

            if not is_replied:
                reply = comment.reply(f"GAME OVER: {error}")
                with open("reply_ids.txt", "a") as f:
                    f.write(f"{reply.id}\n")
    
    # DFS through comments
    for next_comment in comment.replies.list():
        process_comment(g, next_comment)

def main():
    """Main"""

    reddit = praw.Reddit('shiritori-bot')
    subreddit = reddit.subreddit('test')

    while True:
        #g.add_word(input("Enter word: "))
        #print(g.last_word, g.is_alive)

        for submission in subreddit.new(limit=10):
            if submission.title == "SHIRITORI START":
                print("SUBMISSION: " + submission.selftext)
                for comment in submission.comments:
                    # ignore deleted
                    if comment.body == "[deleted]":
                        continue
                
                    g = Game()
                    g.add_word(submission.selftext)
                    process_comment(g, comment)

if __name__ == "__main__":
    main()
