<?php

namespace App\Form;

use App\Entity\Task;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\ChoiceType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;

class TaskUpdateType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options)
    {
        $builder
            ->add("goal")
            ->add("reward")
            ->add("days", ChoiceType::class, [
                "multiple" => true,
                "expanded" => true,
                "choices" => [
                    "Sunday" => "Sunday",
                    "Monday" => "Monday",
                    "Tuesday" => "Tuesday",
                    "Wednesday" => "Wednesday",
                    "Thursday" => "Thursday",
                    "Friday" => "Friday",
                    "Saturday" => "Saturday",
                ]
            ])
        ;
    }

    public function configureOptions(OptionsResolver $resolver)
    {
        $resolver->setDefaults([
            "data_class" => Task::class,
        ]);
    }
}
