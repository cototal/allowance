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

class ImportCommand extends Command
{
    protected static $defaultName = 'app:import';
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
            ->addArgument('filename', InputArgument::REQUIRED, 'Name of the file to import')
            ->addArgument('user1id', InputArgument::REQUIRED, 'ID of user 1')
            ->addArgument('user1email', InputArgument::REQUIRED, 'Email of user 1')
            ->addArgument('user2id', InputArgument::REQUIRED, 'ID of user 2')
        ;
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);
        $filename = $input->getArgument('filename');
        $user1id = $input->getArgument('user1id');
        $user2id = $input->getArgument('user2id');
        $user1email = $input->getArgument('user1email');
        $content = file_get_contents($filename);
        $data = json_decode($content, true);
        $user1 = $this->em->getRepository(User::class)->find($user1id);
        $user2 = $this->em->getRepository(User::class)->find($user2id);
        $count = 0;
        foreach ($data as $item) {
            $user = $item["user"] === $user1email ? $user1 : $user2;
            $entryDate = \DateTimeImmutable::createFromFormat("Y-m-d", $item["entry_date"]);
            $notes = str_replace(['<p>', '</p>'], "", $item["notes"]);
            $entry = (new Entry())
                ->setUser($user)
                ->setEntryDate($entryDate)
                ->setPrice($item["price"])
                ->setCategory($item["category"])
                ->setPayee($item["payee"])
                ->setNotes($notes);
            $this->em->persist($entry);
            ++$count;
        }
        $this->em->flush();

        $io->success("$count records imported");

        return 0;
    }
}
