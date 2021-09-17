<?php

namespace App\Command;

use App\Entity\User;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputArgument;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Input\InputOption;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Question\ConfirmationQuestion;
use Symfony\Component\Console\Question\Question;
use Symfony\Component\Console\Style\SymfonyStyle;
use Symfony\Component\Security\Core\Encoder\UserPasswordEncoderInterface;

class UserUpsertCommand extends Command
{
    protected static $defaultName = 'user:upsert';
    protected static $defaultDescription = 'Create or update a user';
    /**
     * @var EntityManagerInterface
     */
    private $em;
    /**
     * @var UserPasswordEncoderInterface
     */
    private $passwordEncoder;

    public function __construct(EntityManagerInterface $em, UserPasswordEncoderInterface $passwordEncoder)
    {
        $this->em = $em;
        parent::__construct();
        $this->passwordEncoder = $passwordEncoder;
    }

    protected function configure(): void
    {
        $this
            ->setDescription(self::$defaultDescription)
            ->addArgument('username', InputArgument::REQUIRED, 'User username')
        ;
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $helper = $this->getHelper("question");
        $io = new SymfonyStyle($input, $output);
        $username = strtolower($input->getArgument('username'));
        $user = $this->em->getRepository(User::class)->findOneBy(["username" => $username]);
        if (is_null($user)) {
            $user = (new User())->setUsername($username);
            $this->em->persist($user);
        } else {
            $question = new ConfirmationQuestion("User found, change password?", false);
            if (!$helper->ask($input, $output, $question)) {
                return 0;
            }
        }

        $question = new Question("Password:");
        $question->setHidden(true);
        $question->setHiddenFallback(false);
        $password = $helper->ask($input, $output, $question);

        $encodedPassword = $this->passwordEncoder->encodePassword($user, $password);
        $user->setPassword($encodedPassword);

        $this->em->flush();
        $io->success("$username created");

        return 0;
    }
}
