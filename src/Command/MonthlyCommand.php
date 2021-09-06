<?php

namespace App\Command;

use App\Entity\Entry;
use App\Entity\User;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputArgument;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Input\InputOption;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Style\SymfonyStyle;

class MonthlyCommand extends Command
{
    protected static $defaultName = 'app:monthly';
    protected static $defaultDescription = 'Add a short description for your command';

    /**
     * @var EntityManagerInterface
     */
    private $em;

    public function __construct(EntityManagerInterface $em)
    {
        $this->em = $em;
        parent::__construct();
    }

    protected function configure(): void
    {
        $this
            ->setDescription(self::$defaultDescription)
        ;
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);
        $users = $this->em->getRepository(User::class)->findAll();
        $count = 0;
        foreach ($users as $user) {
            $entry = (new Entry())
                ->setUser($user)
                ->setPayee($user->getUsername())
                ->setCategory("Allowance")
                ->setPrice(-100)
                ->setEntryDate(new \DateTimeImmutable());
            $this->em->persist($entry);
            ++$count;
        }
        $this->em->flush();
        $io->success("Allowance applied to $count users");

        return 0;
    }
}
