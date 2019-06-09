import praw
import logging
import sys
import shiritori

def build_response(content):
    """Builds bot response
    """
    response = content
    response += "\n***\n^(I am a bot and I byte)"
    return response

def check_replied(comment):
    """Check if the bot has already replied in the comments
    """
    with open("reply_ids.txt", "r") as f:
        reply_ids = set(f.read().split("\n"))

    # check if comment already replied to
    for c in comment.replies.list():
        if c.id in reply_ids:
            return True
    return False
    

def process_comment(game, comment):
    """Descends and processes replies
    """

    with open("reply_ids.txt", "r") as f:
        reply_ids = set(f.read().split("\n"))

    if comment.id not in reply_ids:

        logging.info(f"Processing comment {comment.id}: {comment.body}")
        
        try:
            g = game.copy()
            g.add_word(comment.body)
        except Exception as error:
            # Process shiritori exception
            if type(error) == shiritori.ShiritoriException:
                if not check_replied(comment):
                    reply = comment.reply(build_response(f"GAME OVER: {error}"))
                    with open("reply_ids.txt", "a") as f:
                        f.write(f"{reply.id}\n")
                        
            # Rethrow otherwise
            else:
                raise
    
    # DFS through comments
    for next_comment in comment.replies.list():
        process_comment(g, next_comment)

def main():
    """Main
    """

    # Logging
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    file_handler = logging.StreamHandler(open("log.txt", "w", encoding="utf-8"))
    file_handler.setFormatter(formatter)
    
    root.addHandler(stdout_handler)
    root.addHandler(file_handler)
    
    
    logging.info("Starting bot...")

    reddit = praw.Reddit('shiritori-bot')
    subreddit = reddit.subreddit('test')

    while True:

        for submission in subreddit.new(limit=10):
            if submission.title == "SHIRITORI START":

                logging.info(f"Processing submission {submission.id}: {submission.selftext}")
                
                for comment in submission.comments:
                    # ignore deleted
                    if comment.body == "[deleted]":
                        continue
                
                    g = shiritori.Game()
                    g.add_word(submission.selftext)
                    process_comment(g, comment)

if __name__ == "__main__":
    main()
