import os
import pygame
from game import Game
import neat
import pickle


class PongGame:
    Num_game = 0

    def __init__(self, window, width, height):
        self.game = Game(window, width, height)
        self.left_paddle = self.game.left_paddle
        self.right_paddle = self.game.right_paddle
        self.ball = self.game.ball

    def test_ai(self, genome, config, ai=True):
        if ai:
            net = neat.nn.FeedForwardNetwork.create(genome, config)

        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break

            if ai:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP]:
                    self.game.move_paddle(left=False, up=True)
                if keys[pygame.K_DOWN]:
                    self.game.move_paddle(left=False, up=False)

                output = net.activate((self.left_paddle.y, self.ball.y, abs(self.left_paddle.x - self.ball.x)))
                decision = output.index(max(output))

                if decision == 0:
                    pass
                elif decision == 1:
                    self.game.move_paddle(left=True, up=True)
                else:
                    self.game.move_paddle(left=True, up=False)

                game_info = self.game.loop()
                self.game.draw()
                pygame.display.update()

            else:
                keys = pygame.key.get_pressed()
                self.handle_paddle_movement_human(keys)

                game_info = self.game.loop()
                self.game.draw()
                pygame.display.update()

            won = False
            if self.game.left_score >= self.game.WINNING_SCORE:
                won = True
                win_text = "Left Player Won!"
            elif self.game.right_score >= self.game.WINNING_SCORE:
                won = True
                win_text = "Right Player Won!"

            if won:
                text = self.game.SCORE_FONT.render(win_text, 1, self.game.RED)
                self.game.window.blit(text, (self.game.window_width // 2 - text.get_width() // 2,
                                             self.game.window_height // 2 - text.get_height() // 2))
                pygame.display.update()
                pygame.time.delay(5000)
                self.game.reset()

        pygame.quit()

    def handle_paddle_movement_human(self, keys):
        if keys[pygame.K_w]:
            self.game.move_paddle(left=True, up=True)
        if keys[pygame.K_s]:
            self.game.move_paddle(left=True, up=False)

        if keys[pygame.K_UP]:
            self.game.move_paddle(left=False, up=True)
        if keys[pygame.K_DOWN]:
            self.game.move_paddle(left=False, up=False)


    def train_ai(self, genome1, genome2, config):
        net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
        net2 = neat.nn.FeedForwardNetwork.create(genome2, config)

        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

            output1 = net1.activate((self.left_paddle.y, self.ball.y, abs(self.left_paddle.x - self.ball.x)))
            decision1 = output1.index(max(output1))

            if decision1 == 0:
                pass
            elif decision1 == 1:
                self.game.move_paddle(left=True, up=True)
                genome1.fitness += 0.01
            else:
                self.game.move_paddle(left=True, up=False)
                genome1.fitness += 0.01

            output2 = net2.activate((self.left_paddle.y, self.ball.y, abs(self.left_paddle.x - self.ball.x)))
            decision2 = output2.index(max(output2))

            if decision2 == 0:
                pass
            elif decision2 == 1:
                self.game.move_paddle(left=False, up=True)
                genome2.fitness += 0.01
            else:
                self.game.move_paddle(left=False, up=False)
                genome2.fitness += 0.01

            game_info = self.game.loop()
            self.game.draw(draw_score=False, draw_hits=True)
            # gen_text = self.game.SCORE_FONT.render(f"Game: {PongGame.Num_game}/50", 1, self.game.WHITE)
            # self.game.window.blit(gen_text, (self.game.window_width // 4 - gen_text.get_width() // 2, 20))
            pygame.display.update()

            if game_info.left_score >= 2 or game_info.right_score >= 2 or game_info.left_hits > 50:
                self.calculate_fitness(genome1, genome2, game_info)
                PongGame.Num_game += 1
                break

    @staticmethod
    def calculate_fitness(genome1, genome2, game_info):
        genome1.fitness += game_info.left_hits
        genome2.fitness += game_info.right_hits


def eval_genomes(genomes, config):
    width, height = 700, 500
    window = pygame.display.set_mode((width, height))

    for i, (genome_id1, genome1) in enumerate(genomes):
        if i == len(genomes) - 1:
            break
        genome1.fitness = 0
        genome_id2, genome2 = genomes[i + 1]
        genome2.fitness = 0 if genome2.fitness is None else genome2.fitness
        game = PongGame(window, width, height)
        game.train_ai(genome1, genome2, config)


def run_neat(config):
    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-9')
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(neat.Checkpointer(10))

    winner = p.run(eval_genomes, 50)
    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)


def test_ai(config, ai=True):
    width, height = 700, 500
    window = pygame.display.set_mode((width, height))

    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)

    game = PongGame(window, width, height)
    if ai:
        game.test_ai(winner, config)
    else:
        game.test_ai(None, None, ai=False)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                         neat.DefaultStagnation, config_path)
    # run_neat(config)
    test_ai(config, ai=False)
