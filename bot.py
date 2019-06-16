import praw
import logging
import sys
import regex as re

import shiritori

def build_response(content):
    """Builds bot response
    """
    
    response = content
    response += "\n***\n^(I am a bot and I byte | [source](https://github.com/jasmaa/shiritori-bot))"
    return response

def check_replied_to(comment):
    """Check if the bot has already replied to a post
    """
    
    with open("replied_ids.txt", "r") as f:
        replied_ids = set(f.read().splitlines())

    # check if comment already replied to
    return comment.id in replied_ids

def is_valid_word(s):
    """Checks if is a Japanese word
    """
    
    return len(s.split()) == 1 and re.match("^[\p{IsHan}\p{IsHira}\p{IsKatakana}]+$", s)


def process_comment(game, comment):
    """Descends and processes replies
    """

    # Only check if not replied to and is a word
    if not check_replied_to(comment) and is_valid_word(comment.body):

        logging.info(f"Processing comment {comment.id}: {comment.body}")
        
        try:
            g = game.copy()
            g.add_word(comment.body)

            # DFS through comments
            for next_comment in comment.replies:
                process_comment(g, next_comment)
                
        except Exception as error:
            # Process shiritori exception
            if type(error) == shiritori.ShiritoriException:
                
                logging.info(f"Replying to comment {comment.id}: {comment.body}")
                
                reply = comment.reply(build_response(f"GAME OVER on {comment.body}: {error}"))
                with open("replied_ids.txt", "a") as f:
                    f.write(f"{comment.id}\n")

            # Rethrow otherwise
            else:
                raise

def main():
    """Main process
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

    with open("replied_ids.txt", "a") as f:
        logging.info("Make sure replied ids file exists")

    reddit = praw.Reddit('shiritori-bot')
    subreddit = reddit.subreddit('test')

    while True:

        for submission in subreddit.new(limit=10):
            if submission.title == "SHIRITORI START" and is_valid_word(submission.selftext):

                try:
                    logging.info(f"Processing submission {submission.id}: {submission.selftext}")
                    
                    g = shiritori.Game()
                    g.add_word(submission.selftext)
                    
                    for comment in submission.comments:
                        # Ignore deleted and non-words
                        if not is_valid_word(submission.selftext):
                            continue

                        process_comment(g, comment)
                        
                except Exception as error:
                    # Process shiritori exception
                    if type(error) == shiritori.ShiritoriException:
                        pass
                    
                    # Rethrow otherwise
                    else:
                        raise

if __name__ == "__main__":
    main()
